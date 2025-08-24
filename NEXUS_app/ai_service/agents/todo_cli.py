#!/usr/bin/env python3
Command Line Interface for TODO Automation System

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

from todo_automation import TodoAutomationSystem
from todo_config import get_agents_config, get_config, load_config_from_file

class TodoCLI:
    """Command Line Interface for TODO AutomationCommand Line Interface for TODO Automation"""
    
    def __init__(self):
        self.parser = self._create_parser()
        self.automation: Optional[TodoAutomationSystem] = None
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the command line argument parserCreate the command line argument parser"""
        parser = argparse.ArgumentParser(
            description="Parallel Agents TODO Automation System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=""""""
Examples:
  # Run automation on current directory
  python todo_cli.py run
  
  # Run with custom configuration
  python todo_cli.py run --config config.json --max-agents 10
  
  # Show progress only
  python todo_cli.py run --progress-only
  
  # Run in specific environment
  python todo_cli.py run --env production
  
  # Show statistics
  python todo_cli.py stats
  
  # List all TODOs
  python todo_cli.py list
            """"""
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Run command
        run_parser = subparsers.add_parser('run', help='Run TODO automation')
        run_parser.add_argument('--directory', '-d', default='.', 
                              help='Directory to scan for TODOs (default: current)')
        run_parser.add_argument('--max-agents', '-m', type=int, default=10,
                              help='Maximum concurrent agents (default: 10)')
        run_parser.add_argument('--config', '-c', 
                              help='Configuration file path')
        run_parser.add_argument('--env', choices=['development', 'testing', 'production'],
                              default='development', help='Environment (default: development)')
        run_parser.add_argument('--progress-only', action='store_true',
                              help='Show progress without detailed output')
        run_parser.add_argument('--output-format', choices=['text', 'json', 'csv'],
                              default='text', help='Output format (default: text)')
        run_parser.add_argument('--timeout', type=float, default=300,
                              help='Processing timeout in seconds (default: 300)')
        
        # Stats command
        stats_parser = subparsers.add_parser('stats', help='Show automation statistics')
        stats_parser.add_argument('--format', choices=['text', 'json', 'csv'],
                                default='text', help='Output format (default: text)')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List all TODOs')
        list_parser.add_argument('--directory', '-d', default='.',
                               help='Directory to scan for TODOs (default: current)')
        list_parser.add_argument('--format', choices=['text', 'json', 'csv'],
                               default='text', help='Output format (default: text)')
        list_parser.add_argument('--priority', type=int, choices=[1, 2, 3, 4, 5],
                               help='Filter by priority level')
        list_parser.add_argument('--status', choices=['pending', 'in_progress', 'completed', 'failed'],
                               help='Filter by status')
        
        # Config command
        config_parser = (
    subparsers.add_parser('config', help='Show or modify configuration')
)
        config_parser.add_argument('--show', action='store_true',
                                 help='Show current configuration')
        config_parser.add_argument('--save', 
                                 help='Save configuration to file')
        config_parser.add_argument('--load',
                                 help='Load configuration from file')
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI with given argumentsRun the CLI with given arguments"""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        try:
            if parsed_args.command == 'run':
                return asyncio.run(self._run_automation(parsed_args))
            elif parsed_args.command == 'stats':
                return self._show_stats(parsed_args)
            elif parsed_args.command == 'list':
                return self._list_todos(parsed_args)
            elif parsed_args.command == 'config':
                return self._handle_config(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}")
                return 1
                
        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user")
            return 130
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    async def _run_automation(self, args) -> int:
        """Run the TODO automationRun the TODO automation"""
        print("🚀 Starting TODO Automation System...")
        
        # Load configuration
        config = self._load_configuration(args)
        
        # Initialize automation system
        self.automation = TodoAutomationSystem(
            max_concurrent_agents=args.max_agents
        )
        
        # Load TODOs
        print(f"📁 Scanning directory: {args.directory}")
        self.automation.load_todos_from_files(args.directory)
        
        if not self.automation.todo_queue:
            print("ℹ️  No TODOs found in the specified directory")
            return 0
        
        print(f"📋 Found {len(self.automation.todo_queue)} TODOs to process")
        print(f"🤖 Using {args.max_agents} concurrent agents")
        
        # Run automation
        if args.progress_only:
            # Run with progress monitoring
            await self._run_with_progress()
        else:
            # Run normally
            await self.automation.run_automation()
        
        return 0
    
    def _load_configuration(self, args) -> dict:
        """Load configuration from various sourcesLoad configuration from various sources"""
        config = {}
        
        # Load environment config
        env_config = get_config(args.env)
        config.update(vars(env_config))
        
        # Load file config if specified
        if args.config:
            file_config = load_config_from_file(args.config)
            config.update(file_config)
        
        # Override with command line arguments
        if args.timeout:
            config['processing_timeout'] = args.timeout
        
        return config
    
    async def _run_with_progress(self):
        """Run automation with progress monitoringRun automation with progress monitoring"""
        print("🔄 Running automation with progress monitoring...")
        
        # Start automation in background
        automation_task = asyncio.create_task(self.automation.run_automation())
        
        # Monitor progress
        try:
            while not automation_task.done():
                progress = self.automation.get_progress_report()
                
                # Clear line and show progress
                print(f"\r🔄 Progress: {progress['completed']}/{progress['total']} completed "
                      f"({progress['processing']} processing) - "
                      f"Queue: {progress['queue_size']}", end='', flush=True)
                
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping automation...")
            # Note: In a real implementation, you'd want to gracefully stop the automation
        
        # Wait for completion
        await automation_task
        
        print("\n✅ Automation completed!")
    
    def _show_stats(self, args) -> int:
        """Show automation statisticsShow automation statistics"""
        if not self.automation:
            print("ℹ️  No automation has been run yet")
            return 0
        
        stats = self.automation.get_progress_report()
        
        if args.format == 'json':
            print(json.dumps(stats, indent=2))
        elif args.format == 'csv':
            self._print_csv_stats(stats)
        else:
            self._print_text_stats(stats)
        
        return 0
    
    def _list_todos(self, args) -> int:
        """List all TODOsList all TODOs"""
        # Create temporary automation instance for listing
        temp_automation = TodoAutomationSystem()
        temp_automation.load_todos_from_files(args.directory)
        
        todos = temp_automation.todo_queue
        
        # Apply filters
        if args.priority:
            todos = [t for t in todos if t.priority == args.priority]
        
        if args.status:
            todos = [t for t in todos if t.status.value == args.status]
        
        if not todos:
            print("ℹ️  No TODOs found matching the criteria")
            return 0
        
        if args.format == 'json':
            todo_data = [self._todo_to_dict(t) for t in todos]
            print(json.dumps(todo_data, indent=2))
        elif args.format == 'csv':
            self._print_csv_todos(todos)
        else:
            self._print_text_todos(todos)
        
        return 0
    
    def _handle_config(self, args) -> int:
        """Handle configuration commandsHandle configuration commands"""
        if args.show:
            config = get_config()
            print("Current Configuration:")
            print(json.dumps(vars(config), indent=2))
        elif args.save:
            config = get_config()
            save_config_to_file(vars(config), args.save)
            print(f"Configuration saved to {args.save}")
        elif args.load:
            config = load_config_from_file(args.load)
            print(f"Configuration loaded from {args.load}")
            print(json.dumps(config, indent=2))
        else:
            print("Use --show, --save, or --load to manage configuration")
        
        return 0
    
    def _todo_to_dict(self, todo) -> dict:
        """Convert TODO item to dictionaryConvert TODO item to dictionary"""
        return {
            'id': todo.id,
            'content': todo.content,
            'file_path': todo.file_path,
            'line_number': todo.line_number,
            'priority': todo.priority,
            'status': todo.status.value,
            'tags': todo.tags
        }
    
    def _print_csv_stats(self, stats: dict):
        """Print statistics in CSV formatPrint statistics in CSV format"""
        print("metric,value")
        for key, value in stats.items():
            if key != 'stats':
                print(f"{key},{value}")
    
    def _print_csv_todos(self, todos: list):
        """Print TODOs in CSV formatPrint TODOs in CSV format"""
        print("id,content,file_path,line_number,priority,status,tags")
        for todo in todos:
            tags_str = ';'.join(todo.tags) if todo.tags else ''
            print(f"{todo.id},{todo.content},{todo.file_path},{todo.line_number},"
                  f"{todo.priority},{todo.status.value},{tags_str}")
    
    def _print_text_stats(self, stats: dict):
        """Print statistics in text formatPrint statistics in text format"""
        print("\n📊 Automation Statistics")
        print("=" * 40)
        print(f"Total Processed: {stats['total']}")
        print(f"Queue Size: {stats['queue_size']}")
        print(f"Currently Processing: {stats['processing']}")
        print(f"Completed: {stats['completed']}")
        print(f"Failed: {stats['failed']}")
    
    def _print_text_todos(self, todos: list):
        """Print TODOs in text formatPrint TODOs in text format"""
        print(f"\n📋 Found {len(todos)} TODOs:")
        print("=" * 60)
        
        for i, todo in enumerate(todos, 1):
            priority_emoji = (
            priority_emoji = "🔴" if todo.priority >= 4 else "🟡" if todo.priority >= 3 else "🟢"
            print(f"{i:2d}. {priority_emoji} Priority {todo.priority}: {todo.content}")
            print(f"    📁 {todo.file_path}:{todo.line_number}")
            if todo.tags:
                print(f"    🏷️  Tags: {', '.join(todo.tags)}")
            print()

def main():
    """Main entry pointMain entry point"""
    cli = TodoCLI()
    sys.exit(cli.run())

if __name__ == "__main__":
    main()
