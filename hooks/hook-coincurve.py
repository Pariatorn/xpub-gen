from PyInstaller.utils.hooks import collect_data_files, copy_metadata

# This hook is necessary because PyInstaller does not automatically
# find the CFFI backend for coincurve.
hiddenimports = ['coincurve._cffi_backend']

# We also need to collect data files associated with coincurve
# and its metadata for pkg_resources to work correctly.
datas = collect_data_files('coincurve')
datas += copy_metadata('coincurve') 