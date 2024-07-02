import asyncio
import os
import tempfile

import alpax


def test_directory() -> None:
    name = "Test"
    unique_id = "test.id"
    with tempfile.TemporaryDirectory() as output_dir:
        path = "test.txt"
        version = "2.3.4"
        with alpax.DirectoryPackWriter(
            output_dir,
            name=name,
            unique_id=unique_id,
            major_version=int(version.split(".")[0]),
            minor_version=int(version.split(".")[1]),
            revision=int(version.split(".")[2]),
        ) as pack_writer:
            pack_writer.set_file_content(path, b"test-content")
            pack_writer.set_preview_content(path, b"test-preview-content")
            pack_writer.set_tags(path, [("Tag Name", ("Tag Value", "Subtag Value"))])

        with open(os.path.join(output_dir, path)) as f:
            assert f.read() == "test-content"
        with open(os.path.join(output_dir, "Ableton Folder Info", "Previews", f"{path}.ogg")) as f:
            assert f.read() == "test-preview-content"

        with open(os.path.join(output_dir, "Ableton Folder Info", "Properties.cfg")) as f:
            properties_text = f.read()
            assert f'String PackUniqueID = "{unique_id}";' in properties_text
            assert f'String PackDisplayName = "{name}";' in properties_text
            for field, value in zip(
                ("PackMajorVersion", "PackMinorVersion", "PackRevision"),
                version.split("."),
            ):
                assert f"Int {field} = {value};" in properties_text

        xmp_files = [
            file for file in os.listdir(os.path.join(output_dir, "Ableton Folder Info")) if file.endswith(".xmp")
        ]
        assert len(xmp_files) == 1

        xmp_file_path = os.path.join(output_dir, "Ableton Folder Info", xmp_files[0])
        with open(xmp_file_path) as xmp_file:
            xmp_content = xmp_file.read()
            assert f"<ablFR:packUniqueId>{unique_id}</ablFR:packUniqueId>" in xmp_content
            assert "<ablFR:packVersion>2.3.4</ablFR:packVersion>" in xmp_content
            assert "<rdf:li>Tag Name|Tag Value|Subtag Value</rdf:li>" in xmp_content


def test_simple_directory_async() -> None:
    with tempfile.TemporaryDirectory() as output_dir:

        async def run() -> None:
            async with alpax.DirectoryPackWriterAsync(output_dir, name="Test", unique_id="test.id") as pack_writer:
                # Simple test, just make sure the write can happen
                # without errors.
                await pack_writer.set_file_content("path.adg", b"content")

        asyncio.run(run())
        with open(os.path.join(output_dir, "path.adg")) as f:
            assert f.read() == "content"
