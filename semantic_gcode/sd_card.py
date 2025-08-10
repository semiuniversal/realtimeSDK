"""
SD card operations for G-code controlled machines.

This module provides a high-level interface for SD card operations,
including file management, print control, and configuration handling.
"""
from typing import Dict, Any, List, Optional, Union, BinaryIO, Callable
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime

from .transport.base import Transport
from .utils.exceptions import TransportError, OperationError


@dataclass
class FileInfo:
    """Information about a file on the SD card."""
    name: str
    size: int
    date: Optional[datetime] = None
    is_directory: bool = False


@dataclass
class PrintStatus:
    """Status of a print job."""
    filename: Optional[str] = None
    progress: float = 0.0  # 0-100%
    layer: Optional[int] = None
    time_elapsed: Optional[float] = None  # seconds
    time_remaining: Optional[float] = None  # seconds
    bytes_printed: Optional[int] = None
    bytes_total: Optional[int] = None


@dataclass
class FileMetadata:
    """Metadata extracted from a G-code file."""
    slicer: Optional[str] = None
    material: Optional[str] = None
    layer_height: Optional[float] = None
    print_time: Optional[float] = None  # seconds
    filament_used: Optional[float] = None  # mm
    layer_count: Optional[int] = None
    build_volume: Optional[Dict[str, float]] = None


class SDCard:
    """
    High-level interface for SD card operations.
    
    This class provides methods for file management, print control,
    and configuration handling on the SD card of a G-code controlled machine.
    """
    
    def __init__(self, transport: Transport):
        """
        Initialize the SD card interface.
        
        Args:
            transport: The transport to use for communication
        """
        self._transport = transport
        self._selected_file: Optional[str] = None
        self._writing_file: Optional[str] = None
        self._print_status: PrintStatus = PrintStatus()
    
    def list_files(self, directory: str = "") -> List[FileInfo]:
        """
        List files on the SD card.
        
        Args:
            directory: The directory to list files from (optional)
            
        Returns:
            List[FileInfo]: A list of file information objects
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # Prepare the command
            command = "M20"
            if directory:
                # Add directory parameter if provided
                command += f" P\"{directory}\""
            
            # Send the command
            response = self._transport.query(command)
            
            if not response:
                return []
            
            # Parse the response
            files = []
            
            # Different firmware versions have different response formats
            if "Begin file list" in response:
                # RepRapFirmware format
                lines = response.splitlines()
                file_lines = [line for line in lines if not line.startswith("Begin") and not line.startswith("End")]
                
                for line in file_lines:
                    # Try to parse the line as a file entry
                    if line.strip():
                        file_info = self._parse_file_entry(line)
                        if file_info:
                            files.append(file_info)
            else:
                # Simple format (one file per line)
                for line in response.splitlines():
                    if line.strip():
                        files.append(FileInfo(name=line.strip(), size=0))
            
            return files
            
        except TransportError as e:
            raise TransportError(f"Failed to list files: {str(e)}")
        except Exception as e:
            raise OperationError(f"Failed to list files: {str(e)}")
    
    def _parse_file_entry(self, line: str) -> Optional[FileInfo]:
        """
        Parse a file entry from the M20 response.
        
        Args:
            line: A line from the M20 response
            
        Returns:
            Optional[FileInfo]: File information, or None if parsing failed
        """
        # Try to parse RepRapFirmware format: "filename.gcode 12345"
        match = re.match(r"([^/]+)\s+(\d+)", line)
        if match:
            return FileInfo(
                name=match.group(1),
                size=int(match.group(2)),
                is_directory=match.group(1).endswith("/")
            )
        
        # Try to parse directory format: "/directory/ 0"
        match = re.match(r"(/\S+/)\s+(\d+)", line)
        if match:
            return FileInfo(
                name=match.group(1),
                size=int(match.group(2)),
                is_directory=True
            )
        
        # Try to parse simple format: "filename.gcode"
        if line.strip():
            return FileInfo(
                name=line.strip(),
                size=0,
                is_directory=line.strip().endswith("/")
            )
        
        return None
    
    def file_exists(self, filename: str) -> bool:
        """
        Check if a file exists on the SD card.
        
        Args:
            filename: The name of the file to check
            
        Returns:
            bool: True if the file exists, False otherwise
        """
        try:
            # Extract directory and filename
            directory = os.path.dirname(filename)
            base_filename = os.path.basename(filename)
            
            # List files in the directory
            files = self.list_files(directory)
            
            # Check if the file exists
            return any(file.name == base_filename for file in files)
            
        except Exception:
            return False
    
    def read_file(self, filename: str) -> str:
        """
        Read the contents of a file from the SD card.
        
        Args:
            filename: The name of the file to read
            
        Returns:
            str: The contents of the file
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # For RepRapFirmware, we can use M36 to get file info
            # and then use M98 to read the file without simulating it
            response = self._transport.query(f"M36 \"{filename}\"")
            
            if not response or "Error" in response:
                raise OperationError(f"Failed to read file: {filename}")
            
            # Try using M98 with P parameter to execute the file
            # This will send the file content to the output without executing it
            # by capturing the response
            response = self._transport.query(f"M98 P\"{filename}\" S-1")
            
            if not response:
                # Fall back to M37 if M98 didn't work
                response = self._transport.query(f"M37 S1 P\"{filename}\"")
                if not response:
                    raise OperationError(f"Failed to read file: {filename}")
            
            # Remove any status lines
            lines = response.splitlines()
            content_lines = [line for line in lines if not line.startswith("ok") and 
                                                       not line.startswith("Error:") and
                                                       not "Simulating" in line and
                                                       not "will print in" in line]
            
            return "\n".join(content_lines)
            
        except TransportError as e:
            raise TransportError(f"Failed to read file: {str(e)}")
        except Exception as e:
            raise OperationError(f"Failed to read file: {str(e)}")
    
    def write_file(self, filename: str, content: str) -> bool:
        """
        Write content to a file on the SD card.
        
        Args:
            filename: The name of the file to write
            content: The content to write to the file
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # Start file write
            response = self._transport.query(f"M28 \"{filename}\"")
            
            if not response or "Error" in response:
                raise OperationError(f"Failed to start file write: {filename}")
            
            # Write the content line by line
            lines = content.splitlines()
            for line in lines:
                self._transport.send_line(line)
            
            # End file write
            response = self._transport.query("M29")
            
            if not response or "Error" in response:
                raise OperationError(f"Failed to end file write: {filename}")
            
            return True
            
        except TransportError as e:
            # Try to close the file if an error occurs
            try:
                self._transport.send_line("M29")
            except Exception:
                pass
            
            raise TransportError(f"Failed to write file: {str(e)}")
        except Exception as e:
            # Try to close the file if an error occurs
            try:
                self._transport.send_line("M29")
            except Exception:
                pass
            
            raise OperationError(f"Failed to write file: {str(e)}")
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from the SD card.
        
        Args:
            filename: The name of the file to delete
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # Send M30 command to delete the file
            response = self._transport.query(f"M30 \"{filename}\"")
            
            if not response or "Error" in response:
                raise OperationError(f"Failed to delete file: {filename}")
            
            return True
            
        except TransportError as e:
            raise TransportError(f"Failed to delete file: {str(e)}")
        except Exception as e:
            raise OperationError(f"Failed to delete file: {str(e)}")
    
    def select_file(self, filename: str) -> bool:
        """
        Select a file for printing.
        
        Args:
            filename: The name of the file to select
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # Send M23 command to select the file
            response = self._transport.query(f"M23 \"{filename}\"")
            
            if not response or "Error" in response:
                raise OperationError(f"Failed to select file: {filename}")
            
            self._selected_file = filename
            return True
            
        except TransportError as e:
            raise TransportError(f"Failed to select file: {str(e)}")
        except Exception as e:
            raise OperationError(f"Failed to select file: {str(e)}")
    
    def start_print(self) -> bool:
        """
        Start printing the selected file.
        
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If no file is selected or the operation fails
        """
        if not self._selected_file:
            raise OperationError("No file selected")
        
        try:
            # Send M24 command to start printing
            response = self._transport.query("M24")
            
            if not response or "Error" in response:
                raise OperationError("Failed to start print")
            
            return True
            
        except TransportError as e:
            raise TransportError(f"Failed to start print: {str(e)}")
        except Exception as e:
            raise OperationError(f"Failed to start print: {str(e)}")
    
    def pause_print(self) -> bool:
        """
        Pause the current print.
        
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # Send M25 command to pause printing
            response = self._transport.query("M25")
            
            if not response or "Error" in response:
                raise OperationError("Failed to pause print")
            
            return True
            
        except TransportError as e:
            raise TransportError(f"Failed to pause print: {str(e)}")
        except Exception as e:
            raise OperationError(f"Failed to pause print: {str(e)}")
    
    def resume_print(self) -> bool:
        """
        Resume the paused print.
        
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # Send M24 command to resume printing
            response = self._transport.query("M24")
            
            if not response or "Error" in response:
                raise OperationError("Failed to resume print")
            
            return True
            
        except TransportError as e:
            raise TransportError(f"Failed to resume print: {str(e)}")
        except Exception as e:
            raise OperationError(f"Failed to resume print: {str(e)}")
    
    def stop_print(self) -> bool:
        """
        Stop the current print.
        
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # Send M0 command to stop printing
            response = self._transport.query("M0")
            
            if not response or "Error" in response:
                raise OperationError("Failed to stop print")
            
            return True
            
        except TransportError as e:
            raise TransportError(f"Failed to stop print: {str(e)}")
        except Exception as e:
            raise OperationError(f"Failed to stop print: {str(e)}")
    
    def get_print_status(self) -> PrintStatus:
        """
        Get the status of the current print.
        
        Returns:
            PrintStatus: The print status
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # Send M27 command to get print status
            response = self._transport.query("M27")
            
            if not response:
                return self._print_status
            
            # Parse the response
            status = PrintStatus()
            status.filename = self._selected_file
            
            # Try to parse RepRapFirmware format
            # Example: "SD printing byte 123456/12345678"
            match = re.search(r"SD printing byte (\d+)/(\d+)", response)
            if match:
                bytes_printed = int(match.group(1))
                bytes_total = int(match.group(2))
                
                status.bytes_printed = bytes_printed
                status.bytes_total = bytes_total
                
                if bytes_total > 0:
                    status.progress = (bytes_printed / bytes_total) * 100
            
            # Update the stored status
            self._print_status = status
            return status
            
        except TransportError as e:
            raise TransportError(f"Failed to get print status: {str(e)}")
        except Exception as e:
            raise OperationError(f"Failed to get print status: {str(e)}")
    
    def create_directory(self, directory: str) -> bool:
        """
        Create a directory on the SD card.
        
        Args:
            directory: The directory to create
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # For RepRapFirmware, we can use M32 with the P parameter
            response = self._transport.query(f"M32 S3 P\"{directory}\"")
            
            if not response or "Error" in response:
                raise OperationError(f"Failed to create directory: {directory}")
            
            return True
            
        except TransportError as e:
            raise TransportError(f"Failed to create directory: {str(e)}")
        except Exception as e:
            raise OperationError(f"Failed to create directory: {str(e)}")
    
    def execute_file(self, filename: str) -> bool:
        """
        Execute a G-code file on the SD card.
        
        Args:
            filename: The name of the file to execute
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # For RepRapFirmware, we can use M32 to execute a file
            response = self._transport.query(f"M32 \"{filename}\"")
            
            if not response or "Error" in response:
                raise OperationError(f"Failed to execute file: {filename}")
            
            return True
            
        except TransportError as e:
            raise TransportError(f"Failed to execute file: {str(e)}")
        except Exception as e:
            raise OperationError(f"Failed to execute file: {str(e)}")
    
    def find_files(self, pattern: str, directory: str = "") -> List[FileInfo]:
        """
        Find files matching a pattern on the SD card.
        
        Args:
            pattern: The pattern to match (e.g., "*.g")
            directory: The directory to search in (optional)
            
        Returns:
            List[FileInfo]: A list of matching files
        """
        try:
            # List files in the directory
            files = self.list_files(directory)
            
            # Convert pattern to regex
            regex_pattern = pattern.replace(".", "\\.").replace("*", ".*")
            
            # Filter files by pattern
            matching_files = [
                file for file in files
                if re.match(regex_pattern, file.name)
            ]
            
            return matching_files
            
        except Exception:
            return []
    
    def get_file_metadata(self, filename: str) -> FileMetadata:
        """
        Get metadata for a G-code file.
        
        Args:
            filename: The name of the file to get metadata for
            
        Returns:
            FileMetadata: The file metadata
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # For RepRapFirmware, we can use M36 to get file info
            response = self._transport.query(f"M36 \"{filename}\"")
            
            if not response or "Error" in response:
                raise OperationError(f"Failed to get file metadata: {filename}")
            
            # Parse the response
            metadata = FileMetadata()
            
            # Try to extract print time
            match = re.search(r"Estimated print time: (\d+)m (\d+)s", response)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                metadata.print_time = minutes * 60 + seconds
            
            # Try to extract filament used
            match = re.search(r"Filament used: (\d+\.?\d*)mm", response)
            if match:
                metadata.filament_used = float(match.group(1))
            
            # Try to extract layer height from file content
            try:
                content = self.read_file(filename)
                
                # Look for slicer comments
                slicer_match = re.search(r"; Generated by ([^\n]+)", content)
                if slicer_match:
                    metadata.slicer = slicer_match.group(1).strip()
                
                # Look for layer height
                layer_height_match = re.search(r"; Layer height: (\d+\.?\d*)", content)
                if layer_height_match:
                    metadata.layer_height = float(layer_height_match.group(1))
                
                # Look for material
                material_match = re.search(r"; Material: ([^\n]+)", content)
                if material_match:
                    metadata.material = material_match.group(1).strip()
                
                # Count layers
                layer_count = len(re.findall(r"; layer \d+,", content))
                if layer_count > 0:
                    metadata.layer_count = layer_count
            except Exception:
                # Ignore errors when reading file content
                pass
            
            return metadata
            
        except TransportError as e:
            raise TransportError(f"Failed to get file metadata: {str(e)}")
        except Exception as e:
            raise OperationError(f"Failed to get file metadata: {str(e)}")
    
    def stream_to_file(
        self,
        remote_filename: str,
        local_file: Union[str, BinaryIO],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """
        Stream content from a local file to a file on the SD card.
        
        Args:
            remote_filename: The name of the file on the SD card
            local_file: The local file path or file-like object
            progress_callback: Optional callback for progress updates
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # Open the local file if a path was provided
            file_obj = None
            if isinstance(local_file, str):
                file_obj = open(local_file, "r")
            else:
                file_obj = local_file
            
            try:
                # Start file write
                response = self._transport.query(f"M28 \"{remote_filename}\"")
                
                if not response or "Error" in response:
                    raise OperationError(f"Failed to start file write: {remote_filename}")
                
                # Get file size for progress reporting
                if hasattr(file_obj, "seek") and hasattr(file_obj, "tell"):
                    file_obj.seek(0, os.SEEK_END)
                    total_size = file_obj.tell()
                    file_obj.seek(0)
                else:
                    total_size = 0
                
                # Write the content line by line
                bytes_written = 0
                for line in file_obj:
                    self._transport.send_line(line.strip())
                    bytes_written += len(line)
                    
                    # Call progress callback if provided
                    if progress_callback and total_size > 0:
                        progress_callback(bytes_written, total_size)
                
                # End file write
                response = self._transport.query("M29")
                
                if not response or "Error" in response:
                    raise OperationError(f"Failed to end file write: {remote_filename}")
                
                return True
                
            finally:
                # Close the file if we opened it
                if isinstance(local_file, str) and file_obj:
                    file_obj.close()
                
        except TransportError as e:
            # Try to close the file if an error occurs
            try:
                self._transport.send_line("M29")
            except Exception:
                pass
            
            raise TransportError(f"Failed to stream to file: {str(e)}")
        except Exception as e:
            # Try to close the file if an error occurs
            try:
                self._transport.send_line("M29")
            except Exception:
                pass
            
            raise OperationError(f"Failed to stream to file: {str(e)}") 
    
    def write_config_file(self, filename: str, content: str) -> bool:
        """
        Write content to a configuration file on the SD card.
        This method is specifically for configuration files and uses M564 to avoid
        triggering print simulation.
        
        Args:
            filename: The name of the file to write
            content: The content to write to the file
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # Start file write with M564 S0 (disable print simulation)
            response = self._transport.query(f"M564 S0")
            if not response or "Error" in response:
                raise OperationError(f"Failed to disable print simulation")
                
            # Start file write
            response = self._transport.query(f"M28 \"{filename}\"")
            
            if not response or "Error" in response:
                raise OperationError(f"Failed to start file write: {filename}")
            
            # Write the content line by line
            lines = content.splitlines()
            for line in lines:
                self._transport.send_line(line)
            
            # End file write
            response = self._transport.query("M29")
            
            if not response or "Error" in response:
                raise OperationError(f"Failed to end file write: {filename}")
            
            # Restore print simulation
            self._transport.query(f"M564 S1")
            
            return True
            
        except TransportError as e:
            # Try to close the file if an error occurs
            try:
                self._transport.send_line("M29")
                self._transport.query(f"M564 S1")  # Restore print simulation
            except Exception:
                pass
            
            raise TransportError(f"Failed to write config file: {str(e)}")
        except Exception as e:
            # Try to close the file if an error occurs
            try:
                self._transport.send_line("M29")
                self._transport.query(f"M564 S1")  # Restore print simulation
            except Exception:
                pass
            
            raise OperationError(f"Failed to write config file: {str(e)}")
    
    def upload_print_file(self, filename: str, content: str) -> bool:
        """
        Upload a print file to the SD card.
        This method is specifically for G-code print files and allows simulation.
        
        Args:
            filename: The name of the file to write
            content: The content to write to the file
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            # Start file write
            response = self._transport.query(f"M28 \"{filename}\"")
            
            if not response or "Error" in response:
                raise OperationError(f"Failed to start file write: {filename}")
            
            # Write the content line by line
            lines = content.splitlines()
            for line in lines:
                self._transport.send_line(line)
            
            # End file write
            response = self._transport.query("M29")
            
            if not response or "Error" in response:
                raise OperationError(f"Failed to end file write: {filename}")
            
            return True
            
        except TransportError as e:
            # Try to close the file if an error occurs
            try:
                self._transport.send_line("M29")
            except Exception:
                pass
            
            raise TransportError(f"Failed to upload print file: {str(e)}")
        except Exception as e:
            # Try to close the file if an error occurs
            try:
                self._transport.send_line("M29")
            except Exception:
                pass
            
            raise OperationError(f"Failed to upload print file: {str(e)}")
    
    def stream_print_file(self, filename: str, local_file_path: str, 
                         progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """
        Stream a print file from local filesystem to the SD card.
        
        Args:
            filename: The name of the file on the SD card
            local_file_path: Path to the local file
            progress_callback: Optional callback for progress updates
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        try:
            with open(local_file_path, 'r') as f:
                # Get file size for progress reporting
                f.seek(0, os.SEEK_END)
                total_size = f.tell()
                f.seek(0)
                
                # Start file write
                response = self._transport.query(f"M28 \"{filename}\"")
                
                if not response or "Error" in response:
                    raise OperationError(f"Failed to start file write: {filename}")
                
                # Write the content line by line
                bytes_written = 0
                for line in f:
                    self._transport.send_line(line.strip())
                    bytes_written += len(line)
                    
                    # Call progress callback if provided
                    if progress_callback and total_size > 0:
                        progress_callback(bytes_written, total_size)
                
                # End file write
                response = self._transport.query("M29")
                
                if not response or "Error" in response:
                    raise OperationError(f"Failed to end file write: {filename}")
                
                return True
                
        except TransportError as e:
            # Try to close the file if an error occurs
            try:
                self._transport.send_line("M29")
            except Exception:
                pass
            
            raise TransportError(f"Failed to stream print file: {str(e)}")
        except Exception as e:
            # Try to close the file if an error occurs
            try:
                self._transport.send_line("M29")
            except Exception:
                pass
            
            raise OperationError(f"Failed to stream print file: {str(e)}") 
    
    def read_config_file(self, filename: str) -> str:
        """
        Read a configuration file using direct HTTP API.
        This method is specifically designed for reading configuration files
        and uses the HTTP API directly for better results.
        
        Args:
            filename: The name of the file to read
            
        Returns:
            str: The contents of the file
            
        Raises:
            TransportError: If communication fails
            OperationError: If the operation fails
        """
        # Check if transport is HTTP
        from .transport.http import HttpTransport
        if not isinstance(self._transport, HttpTransport):
            # Fall back to regular read_file for non-HTTP transports
            return self.read_file(filename)
            
        try:
            # Handle path formatting - remove any leading slash if the path starts with a drive number
            if filename.startswith('/0:'):
                filename = filename[1:]  # Remove leading slash
            elif filename.startswith('0:') and not filename.startswith('0:/'):
                filename = '0:/' + filename[2:]  # Ensure proper format with slash
            elif not filename.startswith('/') and not filename.startswith('0:'):
                # If it doesn't have any prefix, assume it's a relative path
                filename = '0:/sys/' + filename
                print(f"Note: Using path {filename}")
            
            # Get the base URL from the HTTP transport
            base_url = self._transport.base_url
            
            # Use the direct download API
            file_url = f"{base_url}/rr_download?name={filename}"
            
            # Make the request using the transport's session
            response = self._transport._make_request('GET', file_url)
            
            if response.status_code == 404:
                # Try some alternative path formats
                alt_paths = []
                
                # If path starts with 0: but doesn't have the correct format
                if filename.startswith('0:'):
                    if not filename.startswith('0:/'):
                        alt_paths.append('0:/' + filename[2:])
                
                # If path doesn't start with 0: or /, try with 0:/sys/ prefix
                if not filename.startswith('0:') and not filename.startswith('/'):
                    alt_paths.append('0:/sys/' + filename)
                
                # If path starts with /sys/, try with 0: prefix
                if filename.startswith('/sys/'):
                    alt_paths.append('0:' + filename)
                
                # Try each alternative path
                for alt_path in alt_paths:
                    alt_url = f"{base_url}/rr_download?name={alt_path}"
                    alt_response = self._transport._make_request('GET', alt_url)
                    if alt_response.status_code == 200:
                        return alt_response.text
                
                # If all alternatives failed, raise error
                raise OperationError(f"File not found: {filename}. Try one of these formats: '0:/sys/filename.g' or '/sys/filename.g'")
            elif response.status_code != 200:
                raise OperationError(f"Failed to read file: HTTP {response.status_code}")
            
            return response.text
            
        except Exception as e:
            raise OperationError(f"Failed to read config file: {str(e)}") 