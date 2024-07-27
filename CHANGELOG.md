# CHANGELOG

## v0.2.0 (2024-07-27)

### Chore

* chore: add package to isort known first party packages ([`c0d991b`](https://github.com/kmontag/alpax/commit/c0d991b3880903c2984556228bde5b2e2ae516c9))

### Feature

* feat: add output_dir property to directory pack writers ([`afac7e0`](https://github.com/kmontag/alpax/commit/afac7e0e8fb276a92354ca69b4c9ad8d2a8e077c))

### Refactor

* refactor: don&#39;t require a specific context type for pack writers ([`2e3a879`](https://github.com/kmontag/alpax/commit/2e3a879a564239c25613608a8f4669d1ca352935))

## v0.1.1 (2024-07-26)

### Chore

* chore: add generated coverage database to gitignore ([`aa9d824`](https://github.com/kmontag/alpax/commit/aa9d824511d5903a7b36385b086cc255077e70fb))

* chore: fix formatting ([`4ecdfc5`](https://github.com/kmontag/alpax/commit/4ecdfc536d2165cb48e444b7a8ce809b807836ee))

### Ci

* ci: fix coverage artifact names ([`beffde1`](https://github.com/kmontag/alpax/commit/beffde155a816d928a46d4a1105217a7df5fcaa1))

* ci: combine multiple coverage reports ([`ec4e89b`](https://github.com/kmontag/alpax/commit/ec4e89b6bf322dc0798e5e51b2681a4408530f0e))

* ci: update codecov action version ([`4c589f0`](https://github.com/kmontag/alpax/commit/4c589f0983f5bb0fd8de4058d5547004897408f7))

* ci: fail build if codecov fails ([`dbfba64`](https://github.com/kmontag/alpax/commit/dbfba648b8a00075cc559642f72ce5f1bbe9c710))

* ci: upload code coverage in builds ([`bf1edaf`](https://github.com/kmontag/alpax/commit/bf1edaf66cfd090d4f9f8fe131d935b08b299e6a))

### Documentation

* docs: add codecov badge ([`1f5dcc5`](https://github.com/kmontag/alpax/commit/1f5dcc5b7bc64a7d5304dd782d67ea0ec224bfb5))

### Fix

* fix: increase minimum python version to 3.9 ([`6b5d63c`](https://github.com/kmontag/alpax/commit/6b5d63c48f17c0514b45665144cb574d7c7cbaac))

## v0.1.0 (2024-07-22)

### Chore

* chore: add explicit ruff settings to correspond to hatch defaults ([`39662cf`](https://github.com/kmontag/alpax/commit/39662cfce9c617c4de48d08ec8ba258988735329))

### Feature

* feat: accept PathLike argument for directory path output location ([`90b9d02`](https://github.com/kmontag/alpax/commit/90b9d02561d1ce8439602f6caea0052370caa981))

## v0.0.4 (2024-07-07)

### Ci

* ci: replace old project name in github workflow ([`944a781`](https://github.com/kmontag/alpax/commit/944a781e0a9c417d43c09e1176eff05058b6f1b4))

### Documentation

* docs: add python version badge ([`6fd6127`](https://github.com/kmontag/alpax/commit/6fd6127da792dc686ed76d2c9001a54005bceb8d))

### Fix

* fix: add py.typed marker file ([`46ced41`](https://github.com/kmontag/alpax/commit/46ced41f3225a4de14ddd5414e5bbc008930df84))

## v0.0.3 (2024-07-02)

### Refactor

* refactor: rename to alpax (#3) ([`ca74219`](https://github.com/kmontag/alpax/commit/ca7421951fc5b17d2a3c1e817d8f138b86560cc8))

## v0.0.2 (2024-07-02)

### Build

* build: fix detection of semantic release output ([`6b78cfd`](https://github.com/kmontag/alpax/commit/6b78cfdf7fc482f246c34352b9c972f104dd2d56))

* build: install hatch during semantic release execution ([`e3ee436`](https://github.com/kmontag/alpax/commit/e3ee4363122fbec47283bf8812742ffa32a3bdd0))

* build: update semantic release build command ([`bbc20df`](https://github.com/kmontag/alpax/commit/bbc20df150279d3055651952c7692344e16870e5))

* build: use standard actions for PyPi and GitHub Releases publish ([`c73227d`](https://github.com/kmontag/alpax/commit/c73227d3a8f9a2c20ce8a31fa35cd12fdcd950e1))

### Chore

* chore: fixes in semantic release workflow ([`a145bbe`](https://github.com/kmontag/alpax/commit/a145bbe583c4fa0dd252561b8c635e0a23edf2c5))

* chore: update fetch depth in semantic release action ([`dfdd7f6`](https://github.com/kmontag/alpax/commit/dfdd7f69d4d10762b469182a7ed3f0b363a37fb2))

### Documentation

* docs: fix github actions badge ([`c6fb7bf`](https://github.com/kmontag/alpax/commit/c6fb7bf525ce1bce72a21f56c794edfc7359fe87))

### Refactor

* refactor: add semantic release and PyPi upload (#2) ([`be088ec`](https://github.com/kmontag/alpax/commit/be088eceed561ffe7c7a6ceca828682d719224ee))

## v0.0.1 (2024-07-02)

### Unknown

* v0.0.1 ([`11f9beb`](https://github.com/kmontag/alpax/commit/11f9beb244c5ec65004befec4807fc5cd09eee57))

* Add github workflows (#1)

* Add github workflow for testing/linting

* Change test command

* Drop python 3.8, fixes for pre-3.12 versions

* Remove Tuple import

* Rename workflow file, add badge to README ([`f06e324`](https://github.com/kmontag/alpax/commit/f06e3240660f604c810676c686445c97e83bd997))

* Linter fixes ([`258e7f0`](https://github.com/kmontag/alpax/commit/258e7f0bc70c8a10e363189ca50806a534d60e42))

* Bump version ([`bc7d608`](https://github.com/kmontag/alpax/commit/bc7d608d205f04143f9613067431947f28d6a782))

* Fix errors when writing async packs ([`5d4d461`](https://github.com/kmontag/alpax/commit/5d4d461beccd879a164c7615d846c6d14de4e5d2))

* Change package name again, needs to differ sufficiently from &#39;alpacka&#39; ([`e39bfcd`](https://github.com/kmontag/alpax/commit/e39bfcd7c59180fd03c48db59d23dce29eaf0b29))

* Ignore build artifacts ([`ad8e5bf`](https://github.com/kmontag/alpax/commit/ad8e5bf870cdd5946e7fa2913b18fdd3b4262e23))

* Change package name, the original is taken ([`2b713e7`](https://github.com/kmontag/alpax/commit/2b713e7bab13f80edd782caff7f01312aa648907))

* Initial commit ([`8ab60af`](https://github.com/kmontag/alpax/commit/8ab60af515761bf4bb29bb74c677f025294dc2e5))
