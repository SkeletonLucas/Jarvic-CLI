#!/usr/bin/env python3
"""
CLI Jarvis v3.0 - Savage Cyberpunk Terminal Assistant
No APIs (except HTML scraping DuckDuckGo/Wikipedia)
Requires: pip install rich psutil requests beautifulsoup4 prompt_toolkit
"""

import os
import sys
import time
import subprocess
import webbrowser
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Optional

import psutil
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box


class JarvisAssistant:
    """Main Jarvis assistant class with cyberpunk aesthetics"""

    def __init__(self):
        self.console = Console()
        self.running = True

        # Cyberpunk color palette
        self.colors = {
            'primary': '#00ff41',      # Neon green
            'secondary': '#00d9ff',    # Cyan
            'accent': '#ff00ff',       # Magenta
            'warning': '#ffff00',      # Yellow
            'error': '#ff0055',        # Hot pink/red
            'dim': '#808080'           # Gray
        }

        # Witty Jarvis responses
        self.responses = {
            'stats': [
                "Running diagnostics on your digital domain, sir.",
                "Analyzing system vitals. Everything's nominal... mostly.",
                "Scanning the matrix. Numbers incoming.",
            ],
            'network': [
                "Probing the network. Let's see who's talking.",
                "Initiating network reconnaissance, sir.",
                "Mapping your digital connections.",
            ],
            'git': [
                "Checking version control. Hope you committed properly.",
                "Diving into your code history, sir.",
                "Let's see what chaos you've been committing.",
            ],
            'search': [
                "Querying the hive mind. Stand by.",
                "Searching the infinite library, sir.",
                "Let me consult the oracle of search engines.",
            ]
        }

    def show_banner(self):
        """Display cyberpunk ASCII banner on startup"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        ██╗ █████╗ ██████╗ ██╗   ██╗██╗ ██████╗            ║
║        ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝            ║
║        ██║███████║██████╔╝██║   ██║██║██║                 ║
║   ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║██║                 ║
║   ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║╚██████╗            ║
║    ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝ ╚═════╝            ║
║                                                           ║
║            CLI Terminal Assistant v3.0                    ║
║            [ Cyberpunk Savage Edition ]                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style=f"bold {self.colors['primary']}")
        self.console.print(
            f"\nType [bold cyan]help[/bold cyan] for commands or [bold magenta]quit[/bold magenta] to exit.\n",
            style=self.colors['secondary']
        )

    def get_witty_response(self, command: str) -> str:
        if command in self.responses:
            return random.choice(self.responses[command])
        return ""

    async def cmd_stats(self):
        """Live neon pulse bars for CPU, Memory, Disk"""
        self.console.print(f"\n[italic {self.colors['dim']}]{self.get_witty_response('stats')}[/italic {self.colors['dim']}]\n")

        progress = Progress(
            TextColumn("[bold]{task.fields[metric]}[/bold]", justify="right"),
            BarColumn(bar_width=None, complete_style=self.colors['primary']),
            TextColumn("{task.percentage:>5.1f}%"),
            expand=True,
            transient=True
        )

        with Live(progress, refresh_per_second=4, console=self.console):
            cpu_task = progress.add_task("", total=100, metric="CPU")
            mem_task = progress.add_task("", total=100, metric="Memory")
            disk_task = progress.add_task("", total=100, metric="Disk")

            for _ in range(30):  # ~7-8 seconds pulse
                cpu = psutil.cpu_percent(interval=0.2)
                mem = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent

                progress.update(cpu_task, completed=cpu)
                progress.update(mem_task, completed=mem)
                progress.update(disk_task, completed=disk)

                await asyncio.sleep(0.2)

        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        self.console.print(f"\n[bold {self.colors['accent']}]System Uptime:[/bold {self.colors['accent']}] {self._format_uptime(uptime)}\n")

    def cmd_network(self):
        """Show network connections and ping"""
        try:
            self.console.print(f"\n[italic {self.colors['dim']}]{self.get_witty_response('network')}[/italic {self.colors['dim']}]\n")
            table = Table(
                title="[bold]🌐 NETWORK STATUS 🌐[/bold]",
                box=box.DOUBLE_EDGE,
                border_style=self.colors['secondary'],
                title_style=f"bold {self.colors['accent']}"
            )
            table.add_column("Local Address", style=self.colors['primary'])
            table.add_column("Remote Address", style=self.colors['secondary'])
            table.add_column("Status", style=self.colors['accent'])
            table.add_column("PID", style=self.colors['dim'])

            connections = psutil.net_connections(kind='inet')
            for conn in connections[:15]:
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                status = conn.status
                pid = str(conn.pid) if conn.pid else "N/A"
                table.add_row(laddr, raddr, status, pid)

            self.console.print(table)
            self.console.print(f"\n[bold {self.colors['secondary']}]Ping Test:[/bold {self.colors['secondary']}]")
            for target in ["8.8.8.8", "1.1.1.1"]:
                ping_result = self._ping(target)
                if ping_result:
                    self.console.print(f"  [{self.colors['primary']}]✓[/{self.colors['primary']}] {target}: {ping_result}ms")
                else:
                    self.console.print(f"  [{self.colors['error']}]✗[/{self.colors['error']}] {target}: Unreachable")
            self.console.print()
        except Exception as e:
            self._show_error(f"Network scan failed: {str(e)}")

    def cmd_git(self):
        """Git repo status and recent commits"""
        try:
            self.console.print(f"\n[italic {self.colors['dim']}]{self.get_witty_response('git')}[/italic {self.colors['dim']}]\n")
            result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode != 0:
                self.console.print(f"[{self.colors['warning']}]⚠ Not a git repository.[/{self.colors['warning']}]\n")
                return

            branch_result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
            current_branch = branch_result.stdout.strip()

            table = Table(title=f"[bold]📦 GIT STATUS - Branch: {current_branch} 📦[/bold]", box=box.DOUBLE_EDGE,
                          border_style=self.colors['accent'], title_style=f"bold {self.colors['primary']}")
            status_result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)

            if status_result.stdout:
                table.add_column("Status", style=self.colors['accent'])
                table.add_column("File", style=self.colors['secondary'])
                for line in status_result.stdout.strip().split('\n'):
                    if line:
                        status = line[:2].strip()
                        filename = line[3:].strip()
                        table.add_row(status, filename)
                self.console.print(table)
            else:
                self.console.print(f"[{self.colors['primary']}]✓ Working tree clean[/{self.colors['primary']}]")

            commits_result = subprocess.run(['git', 'log', '--pretty=format:%h|%an|%ar|%s', '-5'], capture_output=True, text=True)
            if commits_result.stdout:
                self.console.print(f"\n[bold {self.colors['secondary']}]Recent Commits:[/bold {self.colors['secondary']}]")
                commits_table = Table(box=box.SIMPLE, border_style=self.colors['dim'])
                commits_table.add_column("Hash", style=self.colors['accent'])
                commits_table.add_column("Author", style=self.colors['primary'])
                commits_table.add_column("Time", style=self.colors['secondary'])
                commits_table.add_column("Message", style=self.colors['dim'])
                for line in commits_result.stdout.strip().split('\n'):
                    parts = line.split('|')
                    if len(parts) == 4:
                        commits_table.add_row(*parts)
                self.console.print(commits_table)
            self.console.print()
        except FileNotFoundError:
            self._show_error("Git not installed or not in PATH")
        except Exception as e:
            self._show_error(f"Git operation failed: {str(e)}")

    def cmd_search(self, query: str):
        """DuckDuckGo HTML search without APIs"""
        try:
            if not query:
                self.console.print(f"[{self.colors['warning']}]Usage: search <query>[/{self.colors['warning']}]\n")
                return
            self.console.print(f"\n[italic {self.colors['dim']}]{self.get_witty_response('search')}[/italic {self.colors['dim']}]\n")

            url = f"https://html.duckduckgo.com/html/?q={query}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='result')[:5]
            if not results:
                self.console.print(f"[{self.colors['warning']}]No results found for '{query}'[/{self.colors['warning']}]\n")
                return

            self._last_search_results = []
            for idx, result in enumerate(results, 1):
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                title = title_elem.get_text(strip=True) if title_elem else "No title"
                link = title_elem['href'] if title_elem and 'href' in title_elem.attrs else ""
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No description"
                self._last_search_results.append(link)
                panel = Panel(f"[bold {self.colors['primary']}]{title}[/bold {self.colors['primary']}]\n[{self.colors['dim']}]{snippet}[/{self.colors['dim']}]\n[italic {self.colors['secondary']}]{link}[/{self.colors['secondary']}]",
                              title=f"[{self.colors['dim']}][{idx}][/{self.colors['dim']}]",
                              border_style=self.colors['dim'], box=box.SIMPLE)
                self.console.print(panel)

            self.console.print(f"\n[{self.colors['dim']}]Type 'open <number>' to open a result in browser.[/{self.colors['dim']}]\n")

        except Exception as e:
            self._show_error(f"Search failed: {str(e)}")

    def cmd_open(self, number: str):
        try:
            if not hasattr(self, '_last_search_results'):
                self.console.print(f"[{self.colors['warning']}]No recent search. Use 'search <query>' first.[/{self.colors['warning']}]\n")
                return
            idx = int(number) - 1
            if 0 <= idx < len(self._last_search_results):
                url = self._last_search_results[idx]
                self.console.print(f"[{self.colors['primary']}]Opening result {number} in browser...[/{self.colors['primary']}]\n")
                webbrowser.open(url)
            else:
                self.console.print(f"[{self.colors['error']}]Invalid result number. Choose 1-{len(self._last_search_results)}[/{self.colors['error']}]\n")
        except Exception:
            self.console.print(f"[{self.colors['error']}]Usage: open <number>[/{self.colors['error']}]\n")

    def cmd_clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.show_banner()

    def cmd_help(self):
        help_table = Table(title="[bold]💻 COMMANDS 💻[/bold]", box=box.DOUBLE_EDGE,
                           border_style=self.colors['accent'], title_style=f"bold {self.colors['primary']}")
        help_table.add_column("Command", style=self.colors['secondary'], no_wrap=True)
        help_table.add_column("Description", style=self.colors['dim'])
        commands = [
            ("stats", "Live CPU, RAM, Disk bars"),
            ("network", "Active network connections & ping"),
            ("git", "Git repo status & commits"),
            ("search <query>", "DuckDuckGo search"),
            ("open <number>", "Open search result in browser"),
            ("clear", "Clear terminal & redraw banner"),
            ("help", "Show this help menu"),
            ("quit", "Exit Jarvis"),
        ]
        for cmd, desc in commands:
            help_table.add_row(cmd, desc)
        self.console.print()
        self.console.print(help_table)
        self.console.print()

    def cmd_quit(self):
        self.console.print(f"\n[bold {self.colors['accent']}]Powering down. Until next time, sir.[/bold {self.colors['accent']}]\n")
        self.running = False

    # Helper methods
    def _format_uptime(self, uptime: timedelta) -> str:
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        parts = []
        if days: parts.append(f"{days}d")
        if hours: parts.append(f"{hours}h")
        if minutes: parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return " ".join(parts)

    def _ping(self, host: str) -> Optional[float]:
        try:
            param = '-n' if os.name == 'nt' else '-c'
            command = ['ping', param, '1', host]
            result = subprocess.run(command, capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and 'time=' in result.stdout:
                time_str = result.stdout.split('time=')[1].split()[0]
                return float(time_str.replace('ms', ''))
            return None
        except Exception:
            return None

    def _show_error(self, message: str):
        self.console.print(f"\n[bold {self.colors['error']}]⚠ ERROR: {message}[/bold {self.colors['error']}]\n")

    async def run(self):
        self.cmd_clear()
        while self.running:
            try:
                prompt_text = Text()
                prompt_text.append("jarvis", style=f"bold {self.colors['primary']}")
                prompt_text.append("> ", style=f"bold {self.colors['accent']}")
                self.console.print(prompt_text, end="")
                command_input = input().strip()
                if not command_input: continue
                parts = command_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                if command == 'stats': await self.cmd_stats()
                elif command == 'network': self.cmd_network()
                elif command == 'git': self.cmd_git()
                elif command == 'search': self.cmd_search(args)
                elif command == 'open': self.cmd_open(args)
                elif command == 'clear': self.cmd_clear()
                elif command == 'help': self.cmd_help()
                elif command in ['quit', 'exit']: self.cmd_quit()
                else:
                    self.console.print(f"[{self.colors['error']}]Unknown command: '{command}'. Type 'help' for commands.[/{self.colors['error']}]\n")
            except KeyboardInterrupt:
                self.console.print(f"\n\n[{self.colors['dim']}]Use 'quit' to exit properly.[/{self.colors['dim']}]\n")
            except EOFError:
                self.cmd_quit()
            except Exception as e:
                self._show_error(f"Unexpected error: {str(e)}")


def main():
    jarvis = JarvisAssistant()
    asyncio.run(jarvis.run())


if __name__ == "__main__":
    main()
