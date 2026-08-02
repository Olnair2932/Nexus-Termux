#!/usr/bin/env bash

echo "🛑 Encerrando reprodução..."

pkill -f mpv 2>/dev/null
pkill -f mpg123 2>/dev/null
pkill -f ffplay 2>/dev/null
pkill -f termux-media-player 2>/dev/null
pkill -f vlc 2>/dev/null

termux-media-player stop >/dev/null 2>&1 || true

echo "✅ Reprodução encerrada."
