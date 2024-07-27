from __future__ import annotations

import asyncio
import json
import os
import textwrap
from collections.abc import Collection, Sequence
from contextlib import AsyncExitStack
from typing import (
    TYPE_CHECKING,
    Generic,
    TypedDict,
    TypeVar,
)
from xml.sax.saxutils import escape

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import (
        NotRequired,
        Self,
        TypeAlias,
        Unpack,
        override,
    )
else:
    # Replace the override decorator with a no-op outside of the
    # type-checking environment, so we don't need to depend on
    # `typing_extensions` at runtime.
    def override(func):
        return func


FOLDER_INFO_DIR = "Ableton Folder Info"
PROPERTIES_FILE = "Properties.cfg"

# This appears to be Live's default filename for the first XMP
# (metadata) file in a pack (or the User Library). Unclear exactly
# where the name comes from. .alp files which include an XMP portion
# (e.g. Granulator III) don't seem to include this actual name
# anywhere.
XMP_FILE = "c55d131f-2661-5add-aece-29afb7099dfa.xmp"

# First element is the tag name (e.g. "Character", "Devices"), second
# element is the tag and subtag values.
Tag: TypeAlias = tuple[str, Sequence[str]]

_PackWriterAsyncType = TypeVar("_PackWriterAsyncType", bound="PackWriterAsync")


class PackProperties(TypedDict):
    name: str
    unique_id: str
    vendor: NotRequired[str]
    major_version: NotRequired[int]
    minor_version: NotRequired[int]
    revision: NotRequired[int]
    product_id: NotRequired[int]
    min_software_product_id: NotRequired[int]
    is_hidden_in_browse_groups: NotRequired[bool]


class PackWriterAsync:
    def __init__(self, **k: Unpack[PackProperties]):
        self._name: str = k["name"]
        self._unique_id: str = k["unique_id"]
        self._vendor: str = k.get("vendor", "")

        self._major_version: int = k.get("major_version", 1)
        self._minor_version: int = k.get("minor_version", 0)
        self._revision: int = k.get("revision", 0)

        self._product_id: int = k.get("product_id", 0)
        self._min_software_product_id: int = k.get("min_software_product_id", 0)

        self._is_hidden_in_browse_groups = k.get("is_hidden_in_browse_groups", False)

        self.__exit_stack: AsyncExitStack | None = None

        # Propagate unexpected keys up to `object`, so that errors
        # will be thrown if appropriate.
        for key in PackProperties.__annotations__:
            if key in k:
                del k[key]  # type: ignore

        super().__init__(**k)  # type: ignore

    async def set_file(self, path: str, file: str) -> None:
        raise NotImplementedError

    async def set_file_content(self, path: str, content: bytes) -> None:
        raise NotImplementedError

    async def set_tags(self, path: str, tags: Collection[Tag]) -> None:
        raise NotImplementedError

    async def set_preview(self, path: str, ogg_file: str) -> None:
        raise NotImplementedError

    async def set_preview_content(self, path: str, ogg_content: bytes) -> None:
        raise NotImplementedError

    # Write any pending unwritten content to the output location.
    async def commit(self) -> None:
        raise NotImplementedError

    # Open any resources necessary to start adding content, e.g. a
    # temp directory to stage files. If any resources need to be
    # cleaned up after all content has been added/committed, add them
    # to the exit stack.
    async def _create_context(self, exit_stack: AsyncExitStack) -> None:
        raise NotImplementedError

    async def open(self) -> None:
        if self.__exit_stack is not None:
            msg = f"{self} is already open"
            raise RuntimeError(msg)

        self.__exit_stack = AsyncExitStack()
        await self._create_context(self.__exit_stack)

    async def close(self) -> None:
        exit_stack = self.__exit_stack
        if exit_stack is None:
            msg = f"{self} is not open"
            raise RuntimeError(msg)
        self.__exit_stack = None
        await exit_stack.aclose()

    # Allow usage like:
    #
    #   async with await PackWriterAsync(**args) as p:
    #       await p.set_file(...)
    #       await p.set_preview(...)
    #
    # Which is equivalent to:
    #
    #   p = PackWriterAsync(**args)
    #   await p.open()
    #   try:
    #      await p.set_file(...)
    #      await p.set_preview(...)
    #      await p.commit()
    #   finally:
    #      await p.close(context)
    #
    async def __aenter__(self) -> Self:
        await self.open()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_inst: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type is None:
                await self.commit()
        finally:
            await self.close()


# For synchronous writes, just wrap an async writer.
class PackWriter(Generic[_PackWriterAsyncType]):
    def __init__(self, pack_writer_async: _PackWriterAsyncType) -> None:
        self._pack_writer_async: _PackWriterAsyncType = pack_writer_async

    def set_file(self, path: str, file: str) -> None:
        asyncio.run(self._pack_writer_async.set_file(path, file))

    def set_file_content(self, path: str, content: bytes) -> None:
        asyncio.run(self._pack_writer_async.set_file_content(path, content))

    def set_tags(self, path: str, tags: Collection[Tag]) -> None:
        asyncio.run(self._pack_writer_async.set_tags(path, tags))

    def set_preview(self, path: str, ogg_file: str) -> None:
        asyncio.run(self._pack_writer_async.set_preview(path, ogg_file))

    def set_preview_content(self, path: str, ogg_content: bytes) -> None:
        asyncio.run(self._pack_writer_async.set_preview_content(path, ogg_content))

    def commit(self) -> None:
        asyncio.run(self._pack_writer_async.commit())

    def open(self) -> None:
        asyncio.run(self._pack_writer_async.open())

    def close(self) -> None:
        asyncio.run(self._pack_writer_async.close())

    def __enter__(self) -> Self:
        asyncio.run(self._pack_writer_async.__aenter__())
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        asyncio.run(self._pack_writer_async.__aexit__(exc_type, exc_val, exc_tb))


class DirectoryPackWriterAsync(PackWriterAsync):
    def __init__(self, output_dir: str | os.PathLike, **k: Unpack[PackProperties]):
        super().__init__(**k)

        self._output_dir = output_dir

        # If the output dir exists and is non-empty (or is not a
        # directory), raise an error.
        if os.path.exists(output_dir) and (not os.path.isdir(output_dir) or os.listdir(output_dir)):
            msg = f"Output directory '{output_dir}' exists and is not empty."
            raise ValueError(msg)

        # Keys are paths within the pack.
        self._tags: dict[str, Collection[Tag]] = {}

    @property
    def output_dir(self) -> str | os.PathLike:
        return self._output_dir

    @override
    async def set_file(self, path: str, file: str) -> None:
        await self._copy_to_path(path, file)

    @override
    async def set_file_content(self, path: str, content: bytes) -> None:
        await self._write_to_path(path, content)

    @override
    async def set_tags(self, path: str, tags: Collection[Tag]) -> None:
        self._tags[path] = tags

    @override
    async def set_preview(self, path: str, ogg_file: str) -> None:
        await self._copy_to_path(self._preview_path(path), ogg_file)

    @override
    async def set_preview_content(self, path: str, ogg_content: bytes) -> None:
        await self._write_to_path(self._preview_path(path), ogg_content)

    @override
    async def _create_context(self, exit_stack: AsyncExitStack) -> None:
        pass

    @override
    async def commit(self) -> None:
        await self._write_properties_file()
        if len(self._tags) > 0:
            await self._write_xmp_file()

    async def _write_properties_file(self) -> None:
        text = textwrap.dedent(
            f"""
            Ableton#04I

            FolderConfigData
            {{
              String PackUniqueID = {json.dumps(self._unique_id)};
              String PackDisplayName = {json.dumps(self._name)};
              String PackVendor = {json.dumps(self._vendor)};
              Bool FolderHiddenInBrowseGroups = {'true' if self._is_hidden_in_browse_groups else 'false'};
              Int PackMinorVersion = {self._minor_version};
              Int PackMajorVersion = {self._major_version};
              Int PackRevision = {self._revision};
              Int ProductId = {self._product_id};
              Int MinSoftwareProductId = {self._min_software_product_id};
            }}
            """
        ).lstrip()

        await self._write_to_path(os.path.join(FOLDER_INFO_DIR, PROPERTIES_FILE), text.encode("utf-8"))

    # Write pack metadata, e.g. tags.
    async def _write_xmp_file(self) -> None:
        tags_text = ""
        for path, tags in self._tags.items():
            rdf_items: list[str] = []
            for tag_name, tag_values in tags:
                if len(tag_values) == 0:
                    msg = f"Tag `{tag_name}` is empty for path `{path}`"
                    raise ValueError(msg)
                rdf_items.append("|".join(escape(val) for val in [tag_name, *tag_values]))

            rdf_indent = "               "
            tags_text += textwrap.indent(
                textwrap.dedent(
                    f"""
                    <rdf:li rdf:parseType="Resource">
                       <ablFR:filePath>{escape(path)}</ablFR:filePath>
                       <ablFR:keywords>
                          <rdf:Bag>
                    """
                ).lstrip("\n")
                + "\n".join([f"         <rdf:li>{rdf_item}</rdf:li>" for rdf_item in rdf_items])
                + textwrap.dedent(
                    """
                          </rdf:Bag>
                       </ablFR:keywords>
                    </rdf:li>
                    """
                ),
                rdf_indent,
            )

        xmp_text = textwrap.dedent(
            f"""
            <x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP Core 5.6.0">
               <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                  <rdf:Description rdf:about=""
                        xmlns:dc="http://purl.org/dc/elements/1.1/"
                        xmlns:ablFR="https://ns.ableton.com/xmp/fs-resources/1.0/"
                        xmlns:xmp="http://ns.adobe.com/xap/1.0/">
                     <dc:format>application/vnd.ableton.factory-pack</dc:format>
                     <ablFR:resource>pack</ablFR:resource>
                     <ablFR:platform>mac</ablFR:platform>
                     <ablFR:packUniqueId>{self._unique_id}</ablFR:packUniqueId>
                     <ablFR:packVersion>{self._major_version}.{self._minor_version}.{self._revision}</ablFR:packVersion>
                     <ablFR:items>
                        <rdf:Bag>
            {tags_text}
                        </rdf:Bag>
                     </ablFR:items>
                     <xmp:CreatorTool>Updated by Ableton Index 12.0.1</xmp:CreatorTool>
                     <xmp:CreateDate>2024-03-14T17:40:51-06:00</xmp:CreateDate>
                     <xmp:MetadataDate>2024-03-15T11:55:05-06:00</xmp:MetadataDate>
                  </rdf:Description>
               </rdf:RDF>
            </x:xmpmeta>
            """
        ).lstrip()
        await self._write_to_path(os.path.join(FOLDER_INFO_DIR, XMP_FILE), xmp_text.encode("utf-8"))

    def _preview_path(self, path: str) -> str:
        return os.path.join(FOLDER_INFO_DIR, "Previews", f"{path}.ogg")

    async def _copy_to_path(self, path: str, file: str) -> None:
        def do_copy_file(path: str, file: str) -> None:
            with open(file, "rb") as f:
                asyncio.run(self._write_to_path(path, f.read()))

        await asyncio.to_thread(do_copy_file, path, file)

    async def _write_to_path(self, path: str, content: bytes) -> None:
        def do_write_file(absolute_path: str, content: bytes) -> None:
            os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
            with open(absolute_path, "wb") as f:
                f.write(content)

        absolute_path = os.path.join(self._output_dir, path)
        await asyncio.to_thread(do_write_file, absolute_path, content)


class DirectoryPackWriter(PackWriter[DirectoryPackWriterAsync]):
    def __init__(self, output_dir: str | os.PathLike, **k: Unpack[PackProperties]):
        pack_writer_async = DirectoryPackWriterAsync(output_dir, **k)
        super().__init__(pack_writer_async)

    @property
    def output_dir(self) -> str | os.PathLike:
        return self._pack_writer_async.output_dir
