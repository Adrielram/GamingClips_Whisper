import traceback
import sys
print('PYEXE:', sys.executable)
try:
    import whisperx
    print('whisperx import OK, version:', getattr(whisperx, '__version__', None))
except Exception as e:
    print('whisperx import FAILED')
    traceback.print_exc()
    sys.exit(2)

try:
    print('Attempting to load align model on cuda...')
    align_model, metadata = whisperx.load_align_model(language_code='es', device='cuda')
    print('Loaded align model on cuda: ', type(align_model), 'metadata keys:', list(metadata.keys()) if isinstance(metadata, dict) else type(metadata))
except Exception:
    print('Failed loading align model on cuda, traceback:')
    traceback.print_exc()

try:
    print('Attempting to load align model on cpu...')
    align_model, metadata = whisperx.load_align_model(language_code='es', device='cpu')
    print('Loaded align model on cpu: ', type(align_model), 'metadata keys:', list(metadata.keys()) if isinstance(metadata, dict) else type(metadata))
except Exception:
    print('Failed loading align model on cpu, traceback:')
    traceback.print_exc()

print('Done')
