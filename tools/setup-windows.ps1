# Sofpad design environment setup for Windows 10/11.
# Run in PowerShell: powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1
$ErrorActionPreference = "Continue"

$packages = @(
    @{ Id = "Git.Git";                    Name = "Git" },
    @{ Id = "GitHub.cli";                 Name = "GitHub CLI" },
    @{ Id = "Python.Python.3.12";         Name = "Python 3.12" },
    @{ Id = "OpenSCAD.OpenSCAD";          Name = "OpenSCAD (case CAD)" },
    @{ Id = "KiCad.KiCad";                Name = "KiCad (schematic, PCB, 3D view)" },
    @{ Id = "BlenderFoundation.Blender";  Name = "Blender (renders)" },
    @{ Id = "Prusa3D.PrusaSlicer";        Name = "PrusaSlicer (STL view, slicing)" }
)

foreach ($p in $packages) {
    Write-Host "Install: $($p.Name)"
    winget install --id $p.Id -e --accept-package-agreements --accept-source-agreements --silent
}

Write-Host "Install Python packages"
python -m pip install --upgrade pip
python -m pip install numpy trimesh numpy-stl matplotlib

Write-Host ""
Write-Host "Done. Open a NEW PowerShell window so PATH updates apply."
Write-Host "Check: git --version; gh --version; openscad --version; kicad-cli --version"
Write-Host "Blender and OpenSCAD can be missing from PATH. Use the full install path if needed."
