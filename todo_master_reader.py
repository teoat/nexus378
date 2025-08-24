#!/usr/bin/env python3


    """Enhanced reader for multiple TODO sources
            "TODO_MASTER": project_root / "TODO_MASTER.md",
            "MASTER_TODO": project_root / "nexus" / "master_todo.md"
        }
        
        logger.info(f"TODO Master path: {self.todo_sources['TODO_MASTER']}")

    def get_all_todos(self) -> List[Dict[str, Any]]:
        """Get all TODOs from all sources
                    logger.info(f"Read {len(source_todos)} TODOs from {source_name}")
                except Exception as e:
                    logger.error(f"Error reading from {source_name}: {e}")
            else:
                logger.warning(f"TODO source not found: {source_path}")
        
        logger.info(f"Total TODOs found: {len(all_todos)}")
        return all_todos

    def get_pending_todos(self) -> List[Dict[str, Any]]:
        """Get only pending TODOs from all sources
        """Read TODOs from a specific source file
            logger.info(f"Successfully read {source_name} ({len(content)} characters)")
            
            todos = []
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Parse different TODO formats
                if line.startswith('- [ ]'):
                    # Pending TODO
                    title = line[6:].strip()
                    todos.append({
                        'id': f"{source_name}_{line_num}",
                        'title': title,
                        'source': source_name,
                        'line_number': line_num,
                        'completed': False,
                        'priority': self._detect_priority(title),
                        'extension': self._detect_extension(title)
                    })
                elif line.startswith('- [x]'):
                    # Completed TODO
                    title = line[6:].strip()
                    todos.append({
                        'id': f"{source_name}_{line_num}",
                        'title': title,
                        'source': source_name,
                        'line_number': line_num,
                        'completed': True,
                        'priority': self._detect_priority(title),
                        'extension': self._detect_extension(title)
                    })
            
            logger.info(f"Parsed {len(todos)} TODO items from markdown")
            return todos
            
        except Exception as e:
            logger.error(f"Error reading {source_name}: {e}")
            return []

    def _detect_priority(self, title: str) -> str:
        """Detect priority from TODO title
        """Detect extension from TODO title
        """Get statistics about TODOs