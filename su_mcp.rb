require 'sketchup.rb'
require 'extensions.rb'

module SU_MCP
  unless file_loaded?(__FILE__)
    ex = SketchupExtension.new('Sketchup MCP', 'su_mcp/main')
    ex.description = 'MCP server for Sketchup with furniture design & woodworking tools'
    ex.version     = '1.7.0'
    ex.copyright   = '2024 mhyrr, 2025-2026 dasfink'
    ex.creator     = 'mhyrr (fork: dasfink)'
    Sketchup.register_extension(ex, true)
    file_loaded(__FILE__)
  end
end 