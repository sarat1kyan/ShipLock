#!/usr/bin/env python3
"""
ShipLock - Secure Docker Product Distribution CLI
Production-grade tool for shipping Docker-based products without source code exposure
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.tree import Tree
from rich import box
import os
import sys
from pathlib import Path

console = Console()

# ASCII Art Banner
BANNER = """
[cyan]╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   [bold white]███████╗██╗  ██╗██╗██████╗ ██╗      ██████╗  ██████╗██╗  ██╗[/bold white]   ║
║   [bold white]██╔════╝██║  ██║██║██╔══██╗██║     ██╔═══██╗██╔════╝██║ ██╔╝[/bold white]   ║
║   [bold white]███████╗███████║██║██████╔╝██║     ██║   ██║██║     █████╔╝[/bold white]    ║
║   [bold white]╚════██║██╔══██║██║██╔═══╝ ██║     ██║   ██║██║     ██╔═██╗[/bold white]    ║
║   [bold white]███████║██║  ██║██║██║     ███████╗╚██████╔╝╚██████╗██║  ██╗[/bold white]   ║
║   [bold white]╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝[/bold white]   ║
║                                                       ║
║          [yellow]Secure Docker Distribution Platform v1.0[/yellow]          ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝[/cyan]
"""


class ShipLockCLI:
    def __init__(self):
        self.console = console
        
    def print_banner(self):
        """Display the ShipLock banner"""
        self.console.print(BANNER)
        
    def print_step(self, step_num, total, message):
        """Print a numbered step"""
        self.console.print(f"[bold cyan][[{step_num}/{total}]][/bold cyan] [white]{message}[/white]")
        
    def print_success(self, message):
        """Print success message"""
        self.console.print(f"[bold green]✓[/bold green] {message}")
        
    def print_error(self, message):
        """Print error message"""
        self.console.print(f"[bold red]✗[/bold red] {message}")
        
    def print_warning(self, message):
        """Print warning message"""
        self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")
        
    def print_info(self, message):
        """Print info message"""
        self.console.print(f"[bold blue]ℹ[/bold blue] {message}")


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    ShipLock - Secure Docker Product Distribution
    
    Ship Docker-based products without exposing source code.
    Enterprise-grade licensing and copy protection included.
    """
    pass


@cli.command()
@click.option('--path', '-p', default='.', help='Project directory path')
def init(path):
    """Initialize a new ShipLock project"""
    ui = ShipLockCLI()
    ui.print_banner()
    
    ui.print_step(1, 3, "Initializing ShipLock configuration")
    
    project_path = Path(path).resolve()
    if not project_path.exists():
        ui.print_error(f"Path does not exist: {project_path}")
        sys.exit(1)
    
    # Create .shiplock directory
    shiplock_dir = project_path / '.shiplock'
    shiplock_dir.mkdir(exist_ok=True)
    
    # Create default configuration
    config_file = shiplock_dir / 'config.yaml'
    default_config = """# ShipLock Configuration
project:
  name: my-product
  version: 1.0.0
  
build:
  strip_source: true
  multi_stage: true
  compress: true
  
exclude:
  - "*.py"
  - "*.js"
  - "*.ts"
  - "*.go"
  - "src/"
  - ".git/"
  - "__pycache__/"
  
include:
  - "docker-compose.yml"
  - "Dockerfile"
  - ".env.example"
  
licensing:
  enabled: true
  type: machine_bound
  offline_validation: true
"""
    
    with open(config_file, 'w') as f:
        f.write(default_config)
    
    ui.print_step(2, 3, "Creating .bundleignore file")
    
    bundleignore = project_path / '.bundleignore'
    default_ignore = """# ShipLock Bundle Ignore
# Source code
*.py
*.js
*.ts
*.go
*.java
src/
tests/

# Development files
.git/
.gitignore
.env
*.log
__pycache__/
node_modules/

# Documentation (optional)
docs/
*.md
"""
    
    with open(bundleignore, 'w') as f:
        f.write(default_ignore)
    
    ui.print_step(3, 3, "Project initialized successfully")
    
    # Show summary
    table = Table(title="Initialization Summary", box=box.ROUNDED)
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")
    
    table.add_row(".shiplock/config.yaml", "✓ Created")
    table.add_row(".bundleignore", "✓ Created")
    
    console.print(table)
    ui.print_success("ShipLock project initialized!")
    ui.print_info("Edit .shiplock/config.yaml to customize your build")


@cli.command()
@click.option('--path', '-p', default='.', help='Project directory path')
def analyze(path):
    """Analyze project and show what will be bundled"""
    ui = ShipLockCLI()
    ui.print_banner()
    
    from shiplock_analyzer import ProjectAnalyzer
    
    ui.print_step(1, 4, "Scanning project directory")
    
    analyzer = ProjectAnalyzer(path)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Analyzing project...", total=100)
        
        # Scan files
        progress.update(task, advance=25, description="[cyan]Scanning files...")
        scan_result = analyzer.scan_project()
        
        # Detect Docker
        progress.update(task, advance=25, description="[cyan]Detecting Docker configuration...")
        docker_info = analyzer.detect_docker()
        
        # Analyze dependencies
        progress.update(task, advance=25, description="[cyan]Analyzing dependencies...")
        deps = analyzer.analyze_dependencies()
        
        # Validate
        progress.update(task, advance=25, description="[cyan]Validating configuration...")
        validation = analyzer.validate()
    
    ui.print_step(2, 4, "Project scan complete")
    
    # Display results
    tree = Tree(f"[bold cyan]📦 Project: {scan_result['name']}[/bold cyan]")
    
    docker_branch = tree.add("[yellow]🐳 Docker Configuration[/yellow]")
    if docker_info['has_dockerfile']:
        docker_branch.add("[green]✓ Dockerfile found[/green]")
    if docker_info['has_compose']:
        docker_branch.add(f"[green]✓ docker-compose.yml ({docker_info['services']} services)[/green]")
    
    files_branch = tree.add(f"[yellow]📁 Files ({scan_result['total_files']} total)[/yellow]")
    files_branch.add(f"[green]Include: {scan_result['included_files']} files[/green]")
    files_branch.add(f"[red]Exclude: {scan_result['excluded_files']} files[/red]")
    
    if validation['warnings']:
        warnings_branch = tree.add("[yellow]⚠ Warnings[/yellow]")
        for warning in validation['warnings']:
            warnings_branch.add(f"[yellow]{warning}[/yellow]")
    
    console.print(tree)
    
    ui.print_step(3, 4, "Security analysis")
    
    # Security table
    security_table = Table(title="Security Assessment", box=box.ROUNDED)
    security_table.add_column("Check", style="cyan")
    security_table.add_column("Status", style="white")
    
    security_table.add_row(
        "Source code protection",
        "[green]✓ Enabled[/green]" if validation['source_protected'] else "[red]✗ Disabled[/red]"
    )
    security_table.add_row(
        "Multi-stage build",
        "[green]✓ Detected[/green]" if docker_info['multi_stage'] else "[yellow]⚠ Not detected[/yellow]"
    )
    security_table.add_row(
        "Secrets in .env",
        "[red]✗ Found[/red]" if validation['has_secrets'] else "[green]✓ Clean[/green]"
    )
    
    console.print(security_table)
    
    ui.print_step(4, 4, "Analysis complete")
    
    if validation['ready_to_build']:
        ui.print_success("Project is ready to bundle!")
    else:
        ui.print_warning("Please fix warnings before building")


@cli.command()
@click.option('--path', '-p', default='.', help='Project directory path')
@click.option('--output', '-o', default='./dist', help='Output directory')
@click.option('--zip', 'create_zip', is_flag=True, help='Create ZIP archive')
@click.option('--github', help='Push to GitHub repository')
def build(path, output, create_zip, github):
    """Build secure distributable bundle"""
    ui = ShipLockCLI()
    ui.print_banner()
    
    try:
        from shiplock_builder import BundleBuilder
        
        ui.print_step(1, 6, "Initializing build process")
        
        builder = BundleBuilder(path, output)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            
            # Step 1: Validate
            try:
                task = progress.add_task("[cyan]Validating project...", total=100)
                builder.validate()
                progress.update(task, advance=100)
            except Exception as e:
                ui.print_error(f"Validation failed: {str(e)}")
                console.print_exception()
                sys.exit(1)
            
            ui.print_step(2, 6, "Building Docker images")
            
            # Step 2: Build images
            try:
                task2 = progress.add_task("[cyan]Building Docker images...", total=100)
                builder.build_images()
                progress.update(task2, advance=100)
            except Exception as e:
                ui.print_error(f"Docker build failed: {str(e)}")
                console.print_exception()
                sys.exit(1)
            
            ui.print_step(3, 6, "Stripping source code")
            
            # Step 3: Strip source
            try:
                task3 = progress.add_task("[cyan]Removing source code...", total=100)
                builder.strip_source_code()
                progress.update(task3, advance=100)
            except Exception as e:
                ui.print_error(f"Source stripping failed: {str(e)}")
                console.print_exception()
                sys.exit(1)
            
            ui.print_step(4, 6, "Generating runtime scripts")
            
            # Step 4: Generate runtime
            try:
                task4 = progress.add_task("[cyan]Creating runtime environment...", total=100)
                builder.generate_runtime()
                progress.update(task4, advance=100)
            except Exception as e:
                ui.print_error(f"Runtime generation failed: {str(e)}")
                console.print_exception()
                sys.exit(1)
            
            ui.print_step(5, 6, "Applying security measures")
            
            # Step 5: Security
            try:
                task5 = progress.add_task("[cyan]Applying obfuscation...", total=100)
                builder.apply_security()
                progress.update(task5, advance=100)
            except Exception as e:
                ui.print_warning(f"Security hardening had issues: {str(e)}")
                # Don't fail on security hardening issues, just warn
            
            ui.print_step(6, 6, "Creating distribution package")
            
            # Step 6: Package
            try:
                task6 = progress.add_task("[cyan]Packaging bundle...", total=100)
                
                if create_zip:
                    bundle_path = builder.create_zip_bundle()
                    progress.update(task6, advance=100)
                    ui.print_success(f"ZIP bundle created: {bundle_path}")
                elif github:
                    builder.push_to_github(github)
                    progress.update(task6, advance=100)
                    ui.print_success(f"Pushed to GitHub: {github}")
                else:
                    bundle_path = builder.create_directory_bundle()
                    progress.update(task6, advance=100)
                    ui.print_success(f"Bundle created: {bundle_path}")
            except Exception as e:
                ui.print_error(f"Packaging failed: {str(e)}")
                console.print_exception()
                sys.exit(1)
        
        # Show bundle contents
        bundle_type = 'ZIP Archive' if create_zip else 'Directory'
        if create_zip:
            bundle_loc = str(builder.output_path.parent / f"{Path(path).name}-bundle.zip")
        else:
            bundle_loc = str(builder.output_path)
        
        panel = Panel(
            f"""[green]Build completed successfully![/green]

[cyan]Bundle Location:[/cyan] {bundle_loc}
[cyan]Distribution Type:[/cyan] {bundle_type}

[yellow]Next Steps:[/yellow]
1. Test the bundle: cd {bundle_loc if not create_zip else bundle_loc.rsplit('/', 1)[0]} && ./run.sh
2. Generate license: shiplock license generate --product-id YOUR-PRODUCT --client CLIENT-NAME
3. Deliver to client

[red]Security Reminder:[/red]
• Source code has been stripped
• Images are production-ready
• License verification is active
""",
            title="[bold green]Build Complete[/bold green]",
            border_style="green"
        )
        
        console.print(panel)
        
    except KeyboardInterrupt:
        ui.print_warning("Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        ui.print_error(f"Unexpected error: {str(e)}")
        console.print_exception()
        sys.exit(1)


@cli.group()
def license():
    """License management commands"""
    pass


@license.command('generate')
@click.option('--product-id', required=True, help='Unique product identifier')
@click.option('--client', required=True, help='Client name or identifier')
@click.option('--expires', help='Expiration date (YYYY-MM-DD)')
@click.option('--machine-bound', is_flag=True, default=True, help='Bind to machine fingerprint')
@click.option('--output', '-o', default='./license.key', help='Output license file')
def generate_license(product_id, client, expires, machine_bound, output):
    """Generate a new product license"""
    ui = ShipLockCLI()
    ui.print_banner()
    
    from shiplock_license import LicenseGenerator
    
    ui.print_step(1, 4, "Generating cryptographic keys")
    
    generator = LicenseGenerator()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Creating license...", total=100)
        
        progress.update(task, advance=25, description="[cyan]Generating keys...")
        keys = generator.generate_keys()
        
        progress.update(task, advance=25, description="[cyan]Building license payload...")
        license_data = generator.create_license(
            product_id=product_id,
            client=client,
            expires=expires,
            machine_bound=machine_bound
        )
        
        progress.update(task, advance=25, description="[cyan]Signing license...")
        signed_license = generator.sign_license(license_data)
        
        progress.update(task, advance=25, description="[cyan]Writing license file...")
        generator.write_license(signed_license, output)
    
    ui.print_step(2, 4, "License generated successfully")
    
    # Show license details
    details_table = Table(title="License Details", box=box.ROUNDED)
    details_table.add_column("Property", style="cyan")
    details_table.add_column("Value", style="white")
    
    details_table.add_row("Product ID", product_id)
    details_table.add_row("Client", client)
    details_table.add_row("Expires", expires or "Never")
    details_table.add_row("Machine Bound", "Yes" if machine_bound else "No")
    details_table.add_row("License File", output)
    
    console.print(details_table)
    
    ui.print_step(3, 4, "Saving private key")
    ui.print_warning("Keep the private key secure - it's required for future license generation!")
    
    ui.print_step(4, 4, "License ready for distribution")
    
    panel = Panel(
        f"""[green]License created successfully![/green]

[cyan]License File:[/cyan] {output}
[cyan]Public Key:[/cyan] shiplock_public.key
[cyan]Private Key:[/cyan] shiplock_private.key

[yellow]Distribution Instructions:[/yellow]
1. Include license file in bundle
2. Client activates with: ./activate_license.sh
3. Product verifies on startup

[red]Security Notes:[/red]
• Private key must be kept secret
• License is cryptographically signed
• Machine binding prevents sharing
""",
        title="[bold green]License Generated[/bold green]",
        border_style="green"
    )
    
    console.print(panel)


@license.command('verify')
@click.argument('license_file')
def verify_license(license_file):
    """Verify a license file"""
    ui = ShipLockCLI()
    ui.print_banner()
    
    try:
        from shiplock_license import LicenseVerifier
        
        ui.print_step(1, 3, "Loading license file")
        
        # Check if file exists
        license_path = Path(license_file)
        if not license_path.exists():
            ui.print_error(f"License file not found: {license_file}")
            sys.exit(1)
        
        verifier = LicenseVerifier()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("[cyan]Verifying license...", total=100)
            
            progress.update(task, advance=33, description="[cyan]Checking signature...")
            is_valid, details = verifier.verify(str(license_path))
            
            progress.update(task, advance=33, description="[cyan]Validating expiration...")
            
            progress.update(task, advance=34, description="[cyan]Checking machine binding...")
        
        ui.print_step(2, 3, "Verification complete")
        
        if is_valid:
            ui.print_success("License is VALID")
            
            details_table = Table(title="License Information", box=box.ROUNDED)
            details_table.add_column("Property", style="cyan")
            details_table.add_column("Value", style="green")
            
            # Format license details nicely
            display_map = {
                'license_id': 'License ID',
                'product_id': 'Product ID',
                'client': 'Client',
                'issued_at': 'Issued At',
                'expires_at': 'Expires At',
                'machine_bound': 'Machine Bound',
                'features': 'Features'
            }
            
            for key, value in details.items():
                display_key = display_map.get(key, key.replace('_', ' ').title())
                
                # Format values
                if key == 'features' and isinstance(value, dict):
                    if value:
                        formatted_value = ', '.join(value.keys())
                    else:
                        formatted_value = 'None'
                elif key == 'machine_bound':
                    formatted_value = 'Yes' if value else 'No'
                elif key in ['issued_at', 'expires_at']:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        formatted_value = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        formatted_value = str(value)
                else:
                    formatted_value = str(value)
                
                details_table.add_row(display_key, formatted_value)
            
            console.print(details_table)
            sys.exit(0)
        else:
            ui.print_error("License is INVALID")
            reason = details.get('reason', 'Unknown error')
            ui.print_warning(f"Reason: {reason}")
            
            # Show additional details if available
            if len(details) > 1:
                error_table = Table(title="Error Details", box=box.ROUNDED, border_style="red")
                error_table.add_column("Property", style="cyan")
                error_table.add_column("Value", style="red")
                
                for key, value in details.items():
                    if key != 'reason':
                        error_table.add_row(key.replace('_', ' ').title(), str(value))
                
                console.print(error_table)
            
            sys.exit(1)
    
    except Exception as e:
        ui.print_error(f"Verification failed: {str(e)}")
        console.print_exception()
        sys.exit(1)


if __name__ == '__main__':
    cli()
