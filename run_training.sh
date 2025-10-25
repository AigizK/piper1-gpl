python3 -m piper.train fit \
  --data.voice_name "homai" \
  --data.csv_path /home/aigiz/stable_tts/data/homai_lj_train.txt \
  --data.audio_dir /home/aigiz/stable_tts/data/audio/ \
  --model.sample_rate 22050 \
  --data.espeak_voice "en-us" \
  --data.cache_dir /home/aigiz/tts_cache_dir/ \
  --data.config_path /home/aigiz/piper1-gpl/config.json \
  --data.batch_size 32 \
  --ckpt_path /home/aigiz/piper1-gpl/ckpt_path/finetune.ckpt