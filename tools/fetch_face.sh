#!/usr/bin/env bash
# Re-download face-api.js + weights into face/ (run from the repo root)
set -e; B=https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master; mkdir -p face/models
curl -sSfL -o face/face-api.min.js $B/dist/face-api.min.js
for f in tiny_face_detector_model-weights_manifest.json tiny_face_detector_model-shard1 face_landmark_68_tiny_model-weights_manifest.json face_landmark_68_tiny_model-shard1 face_recognition_model-weights_manifest.json face_recognition_model-shard1 face_recognition_model-shard2; do curl -sSfL -o face/models/$f $B/weights/$f; done
echo "face/ ready"
