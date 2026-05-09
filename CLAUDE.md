# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ExploreFinance is an Obsidian vault for personal finance and investment knowledge management. The project documents learning materials, research notes, and practical frameworks for ETF investment in the Chinese securities market. Content is primarily in Simplified Chinese.

## Repository Type

This is an Obsidian knowledge base, not a traditional software project. There are no build, test, or lint commands. The repository is version-controlled via the Obsidian Git plugin for automatic backup.

## Directory Structure

The vault follows a three-pillar architecture aligned with investment learning goals:

- **扎实基础/** - Foundational knowledge: economics, investment theory, derivatives, quantitative finance
- **立足行业/** - Industry knowledge: regulations, current events (Caixin articles), legal compliance
- **投资技能/** - Practical investment skills: macro analysis, financial statement reading, industry analysis, fund investment, valuation methods, asset allocation

Additional folders:
- **读书笔记/** - Book reading notes
- **研报阅读/** - Research report analysis
- **周刊素材/** - Weekly newsletter materials
- **学习方法/** - Learning methodology notes
- **沟通方法/** - Communication skills
- **管理知识/** - Management knowledge
- **积极心理学/** - Positive psychology

## Obsidian Configuration

- Vim mode enabled
- Live preview mode
- Attachments stored in `./attachment` subfolder relative to notes
- New files created in current folder

## Key Plugins

- **obsidian-git**: Automatic version control and backup
- **dataview**: Query and display notes as data
- **templater-obsidian**: Template automation
- **obsidian-tasks-plugin**: Task management with TODO syntax
- **periodic-notes**: Daily/weekly/monthly notes
- **quickadd**: Quick note capture
- **obsidian-hypothesis-plugin**: Web article annotations via Hypothes.is

## File Conventions

- Notes use standard Markdown with Obsidian-flavored extensions
- Wikilinks format: `[[filename]]` for internal links
- Chinese filenames and content throughout
- PDF attachments stored alongside notes in `attachment` subfolders

## Working with This Vault

When editing or creating notes:
1. Maintain consistency with existing Chinese terminology
2. Use relative links for attachments: `attachment/filename.pdf`
3. Preserve frontmatter metadata if present
4. Follow the existing folder organization by topic area
