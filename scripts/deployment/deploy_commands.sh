#!/bin/bash
# Deployment Commands for Chapter Summary System
# Run these commands to deploy to VM

echo "=========================================="
echo "Deploying Chapter Summary System to VM"
echo "=========================================="

# Step 1: Upload new prompt file
echo ""
echo "Step 1: Uploading chapter_summary_extract.txt..."
scp scripts/deployment/prompts/chapter_summary_extract.txt \
    ketuakali@36.93.133.244:/home/ketuakali/va/VA/qa/scripts/deployment/prompts/

# Step 2: Upload modified API files
echo ""
echo "Step 2: Uploading modified API files..."
scp scripts/deployment/api/chapter_context_generator.py \
    ketuakali@36.93.133.244:/home/ketuakali/va/VA/qa/scripts/deployment/api/

scp scripts/deployment/api/conversation_manager.py \
    ketuakali@36.93.133.244:/home/ketuakali/va/VA/qa/scripts/deployment/api/

# Step 3: Restart bot
echo ""
echo "Step 3: Restarting quran-bot service..."
ssh ketuakali@36.93.133.244 "sudo systemctl restart quran-bot"

# Step 4: Check status
echo ""
echo "Step 4: Checking bot status..."
ssh ketuakali@36.93.133.244 "sudo systemctl status quran-bot --no-pager"

echo ""
echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
echo ""
echo "Monitor logs with:"
echo "  ssh ketuakali@36.93.133.244"
echo "  journalctl -u quran-bot -f"
echo ""
echo "Look for:"
echo "  - 'Extracting chapter summary...'"
echo "  - '[!] Cached chapter missing summary...'"
echo "  - '[OK] Summary extracted'"
echo ""
