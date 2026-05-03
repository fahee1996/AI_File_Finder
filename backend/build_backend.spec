# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect all ChromaDB submodules
chromadb_imports = collect_submodules('chromadb')

# Collect all data files from chromadb
datas = []
binaries = []

# Collect chromadb
tmp_ret = collect_all('chromadb')
datas += tmp_ret[0]
binaries += tmp_ret[1]

# Collect sentence_transformers
tmp_ret = collect_all('sentence_transformers')
datas += tmp_ret[0]
binaries += tmp_ret[1]

# Add our own files
datas += [
    ('*.py', '.'),
    ('api/*.py', 'api'),
    ('indexer/*.py', 'indexer'),
    ('search/*.py', 'search'),
    ('llm/*.py', 'llm'),
    ('operations/*.py', 'operations'),
    ('utils/*.py', 'utils'),
]

a = Analysis(
    ['http_server.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        # Flask
        'flask',
        'flask_cors',
        'werkzeug',
        
        # Ollama
        'ollama',
        
        # ChromaDB - ALL modules
        'chromadb',
        'chromadb.api',
        'chromadb.config',
        'chromadb.db',
        'chromadb.telemetry',
        'chromadb.telemetry.product',
        'chromadb.telemetry.product.posthog',
        'chromadb.server',
        'chromadb.server.fastapi',
        'chromadb.utils',
        
        # Sentence Transformers
        'sentence_transformers',
        'torch',
        'transformers',
        'tokenizers',
        'tqdm',
        'numpy',
        'scipy',
        'sklearn',
        'PIL',
        
        # File processing
        'PyPDF2',
        'docx',
        'openpyxl',
        'watchdog',
        'pyperclip',
        'send2trash',
        
        # Other
        'sqlite3',
        'json',
        'pathlib',
    ] + chromadb_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AIFileFinderBackend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AIFileFinderBackend',
)