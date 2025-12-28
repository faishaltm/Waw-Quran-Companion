#!/bin/bash
# Deployment Script for Chapter Context Refactoring + Ruku to Section Migration
# Author: Claude
# Date: 2025-01-15

set -e  # Exit on error

SSH_KEY="$HOME/.ssh/id_rsa_vm"
VM_USER="ketuakali"
VM_HOST="36.93.133.244"
REMOTE_BASE="/home/ketuakali/va/VA/qa/scripts/deployment"
LOCAL_BASE="D:/Script/Project/quran/scripts/deployment"

echo "=========================================="
echo "DEPLOYING REFACTORED CHAPTER CONTEXT"
echo "Part 1: Simplified JSON (only user_introduction)"
echo "Part 2: Ruku to Section Headings"
echo "=========================================="
echo ""

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "ERROR: SSH key not found at $SSH_KEY"
    exit 1
fi

echo "Using SSH key: $SSH_KEY"
echo "Target: $VM_USER@$VM_HOST"
echo ""

# Step 1: Upload updated prompt files
echo "[Step 1/7] Uploading updated prompt files..."
scp -i "$SSH_KEY" \
    "$LOCAL_BASE/prompts/chapter_context_short.txt" \
    "$VM_USER@$VM_HOST:$REMOTE_BASE/prompts/"
echo "  - chapter_context_short.txt uploaded"

scp -i "$SSH_KEY" \
    "$LOCAL_BASE/prompts/chapter_context_long.txt" \
    "$VM_USER@$VM_HOST:$REMOTE_BASE/prompts/"
echo "  - chapter_context_long.txt uploaded"

# Step 2: Delete old prompt file (no longer needed)
echo ""
echo "[Step 2/7] Removing obsolete prompt file..."
ssh -i "$SSH_KEY" "$VM_USER@$VM_HOST" \
    "rm -f $REMOTE_BASE/prompts/chapter_summary_extract.txt && echo '  - chapter_summary_extract.txt deleted' || echo '  - file not found (OK)'"

# Step 3: Upload modified API files
echo ""
echo "[Step 3/7] Uploading modified API files..."
scp -i "$SSH_KEY" \
    "$LOCAL_BASE/api/chapter_context_generator.py" \
    "$VM_USER@$VM_HOST:$REMOTE_BASE/api/"
echo "  - chapter_context_generator.py uploaded"

scp -i "$SSH_KEY" \
    "$LOCAL_BASE/api/conversation_manager.py" \
    "$VM_USER@$VM_HOST:$REMOTE_BASE/api/"
echo "  - conversation_manager.py uploaded"

# Step 4: Upload NEW section_session_manager.py
echo ""
echo "[Step 4/7] Uploading NEW section_session_manager.py..."
scp -i "$SSH_KEY" \
    "$LOCAL_BASE/api/section_session_manager.py" \
    "$VM_USER@$VM_HOST:$REMOTE_BASE/api/"
echo "  - section_session_manager.py uploaded (NEW FILE)"

# Step 5: Upload refactored bot
echo ""
echo "[Step 5/7] Uploading refactored Telegram bot..."
scp -i "$SSH_KEY" \
    "$LOCAL_BASE/quran_telegram_bot.py" \
    "$VM_USER@$VM_HOST:$REMOTE_BASE/"
echo "  - quran_telegram_bot.py uploaded"

# Step 6: Backup old cache (optional but recommended)
echo ""
echo "[Step 6/7] Backing up old cache..."
ssh -i "$SSH_KEY" "$VM_USER@$VM_HOST" \
    "cd $REMOTE_BASE && mkdir -p cache_backup_$(date +%Y%m%d) && cp -r cache/*.json cache_backup_$(date +%Y%m%d)/ 2>/dev/null && echo '  - Cache backed up' || echo '  - No cache to backup (OK)'"

# Step 7: Restart bot service
echo ""
echo "[Step 7/7] Restarting quran-bot service..."
ssh -i "$SSH_KEY" "$VM_USER@$VM_HOST" "sudo systemctl restart quran-bot"
echo "  - Service restarted"

# Wait a moment for service to start
sleep 3

# Check status
echo ""
echo "=========================================="
echo "Checking bot status..."
echo "=========================================="
ssh -i "$SSH_KEY" "$VM_USER@$VM_HOST" "sudo systemctl status quran-bot --no-pager -n 20"

echo ""
echo "=========================================="
echo "DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "What changed:"
echo "  1. Chapter context now outputs ONLY user_introduction (comprehensive)"
echo "  2. Switched from Ruku (556) to Section Headings (1966)"
echo "  3. Section headings are descriptive (e.g., 'Qualities of the Believers')"
echo "  4. Conversation initializes with user_introduction as first message"
echo ""
echo "Monitor logs with:"
echo "  ssh -i $SSH_KEY $VM_USER@$VM_HOST"
echo "  journalctl -u quran-bot -f"
echo ""
echo "Test with Telegram:"
echo "  /surah 68"
echo "  -> Should show user_introduction + section overview"
echo "  /next"
echo "  -> Should show Section 1 with heading"
echo ""
echo "Old cache will auto-regenerate when accessed."
echo ""
