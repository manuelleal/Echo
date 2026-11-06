"""Duración de los audios pregrabados (ninguno debe estar vacío)."""
import glob
import sys

import soundfile as sf

d = sorted((sf.info(f).duration, f) for f in glob.glob(sys.argv[1] + "/*.wav"))
print("n", len(d), "min", round(d[0][0], 2), "s", "max", round(d[-1][0], 2), "s")
