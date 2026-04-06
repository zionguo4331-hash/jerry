#!/bin/bash

# 同步脚本 - opencode 项目同步到 Obsidian 知识库
# 路径: /Users/guoruijie/Documents/GitHub/jerry/sync.sh

SOURCE_DIR="/Users/guoruijie/Documents/GitHub/jerry"
OBSIDIAN_DIR="/Users/guoruijie/Documents/知识库/opencode工作区"
CODE_DIR="$OBSIDIAN_DIR/代码库"
NOTE_DIR="$OBSIDIAN_DIR/笔记库"
KNOWLEDGE_DIR="/Users/guoruijie/Documents/知识库"

echo "=== 开始同步 $(date) ==="

# 创建目录
mkdir -p "$CODE_DIR" "$NOTE_DIR"

# 同步代码文件
for ext in js py ts json html css xml yaml yml sh; do
    find "$SOURCE_DIR" -maxdepth 3 -name "*.$ext" -type f 2>/dev/null | while read -r file; do
        dest_file="$CODE_DIR/$(basename "$file")"
        if [ ! -f "$dest_file" ] || [ "$file" -nt "$dest_file" ]; then
            cp "$file" "$dest_file"
            echo "复制: $file -> $CODE_DIR"
        fi
    done
done

# 同步 Markdown 文件
find "$SOURCE_DIR" -maxdepth 3 -name "*.md" -type f 2>/dev/null | while read -r file; do
    dest_file="$NOTE_DIR/$(basename "$file")"
    if [ ! -f "$dest_file" ] || [ "$file" -nt "$dest_file" ]; then
        cp "$file" "$dest_file"
        echo "复制: $file -> $NOTE_DIR"
    fi
done

# Git 提交并推送
cd "$KNOWLEDGE_DIR"
git add opencode工作区/
git commit -m "同步: $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null
git push origin main 2>/dev/null

echo "=== 同步完成 $(date) ==="
