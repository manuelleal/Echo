"""Lanza y detiene llama-server en 127.0.0.1:8097 (sólo localhost, sin internet).

Uso como módulo:
    from tutor.servidor import Servidor
    with Servidor(hilos=4) as s:
        ...  # s.url == "http://127.0.0.1:8097"

Uso por consola:
    python -m tutor.servidor --hilos 4      # arranca, espera /health y queda en pie hasta Ctrl+C
"""
import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODELOS = Path(os.environ.get("TUTOR_MODELOS_DIR", r"C:\Users\User\Documents\PROYECTOS\JUACO-MODELOS"))
EXE = Path(os.environ.get("TUTOR_LLAMA_SERVER", MODELOS / "llama_cpp" / "llama-server.exe"))
MODELO = Path(os.environ.get("TUTOR_MODELO", MODELOS / "modelos" / "qwen2.5-1.5b-instruct-q4_k_m.gguf"))
HOST = "127.0.0.1"
PUERTO = int(os.environ.get("TUTOR_PUERTO", "8097"))
URL = f"http://{HOST}:{PUERTO}"


def salud(url: str = URL, espera_s: float = 1.0) -> bool:
    """True si /health responde 200 (modelo cargado)."""
    try:
        with urllib.request.urlopen(url + "/health", timeout=espera_s) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError, ValueError):
        return False


class Servidor:
    """Proceso llama-server propio. Sólo detiene el proceso que él mismo lanzó."""

    def __init__(self, hilos: int = 4, contexto: int = 2048, puerto: int = PUERTO):
        self.hilos = hilos
        self.contexto = contexto
        self.puerto = puerto
        self.url = f"http://{HOST}:{puerto}"
        self.proc = None
        self.log_path = RAIZ / "datos" / f"servidor_t{hilos}.log"
        self.segundos_arranque = None

    def comando(self):
        return [
            str(EXE), "-m", str(MODELO),
            "--host", HOST, "--port", str(self.puerto),
            "-t", str(self.hilos), "-c", str(self.contexto), "-np", "1",
            "--no-webui",
        ]

    def iniciar(self, tope_s: float = 120.0):
        if salud(self.url):
            raise RuntimeError(
                f"Ya hay un servidor respondiendo en {self.url}; no lanzo otro "
                "(usa ese o detenlo tú: este módulo sólo detiene lo que lanza)."
            )
        if not EXE.exists() or not MODELO.exists():
            raise FileNotFoundError(f"Falta el motor o el modelo: {EXE} / {MODELO}")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        log = open(self.log_path, "w", encoding="utf-8", errors="replace")
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        t0 = time.time()
        self.proc = subprocess.Popen(self.comando(), stdout=log, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, creationflags=flags)
        self._log = log
        while time.time() - t0 < tope_s:
            if self.proc.poll() is not None:
                raise RuntimeError(f"llama-server terminó al arrancar (código {self.proc.returncode}); ver {self.log_path}")
            if salud(self.url, 0.5):
                self.segundos_arranque = round(time.time() - t0, 2)
                return self
            time.sleep(0.25)
        self.detener()
        raise TimeoutError(f"llama-server no respondió /health en {tope_s} s")

    def detener(self):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=10)
        self.proc = None
        if getattr(self, "_log", None):
            self._log.close()
            self._log = None

    def __enter__(self):
        return self.iniciar()

    def __exit__(self, *a):
        self.detener()


def main():
    ap = argparse.ArgumentParser(description="Arranca llama-server local para el tutor")
    ap.add_argument("--hilos", type=int, default=4)
    a = ap.parse_args()
    with Servidor(hilos=a.hilos) as s:
        print(f"llama-server listo en {s.url} ({s.segundos_arranque} s, {a.hilos} hilos). Ctrl+C para detener.")
        try:
            while s.proc.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    print("detenido")


if __name__ == "__main__":
    main()
