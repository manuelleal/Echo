#!/bin/bash
# En candy: desempaca los audios pregrabados y reinicia la demo.
cd ~/f2/biblioteca/demo || exit 1
tar xzf audio_tutor.tgz && rm -f audio_tutor.tgz
echo "audios: $(ls audio | wc -l)"
bash arranca_demo.sh 2>&1 | tail -1
