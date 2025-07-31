--[[
# MIT License
#
# Copyright (c) 2025 Mickaël Canouil
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
]]

--- Pandoc utility function for stringifying elements
--- @type function
local stringify = pandoc.utils.stringify

--- Flag to track if deprecation warning has been shown
--- @type boolean
local deprecation_warning_shown = false

--- Check if a string is empty or nil.
--- @param s string|nil The string to check
--- @return boolean True if the string is nil or empty, false otherwise
local function is_empty(s)
  return s == nil or s == ''
end

--- Default configuration for preview colour features
--- @type table<string, boolean>
local preview_colour_meta = {
  ["text"] = false,
  ["code"] = true
}

--- Check for deprecated top-level preview-colour configuration and emit warning.
--- @param meta table<string, any> Document metadata table
--- @param key string The configuration key being accessed
--- @return boolean|nil The value from deprecated config, or nil if not found
local function check_deprecated_config(meta, key)
  if not is_empty(meta['preview-colour']) and not is_empty(meta['preview-colour'][key]) then
    if not deprecation_warning_shown then
      quarto.log.warning(
        'Top-level "preview-colour" configuration is deprecated. ' ..
        'Please use:\n' ..
        'extensions:\n' ..
        '  preview-colour:\n' ..
        '    ' .. key .. ': value'
      )
      deprecation_warning_shown = true
    end
    return meta['preview-colour'][key]
  end
  return nil
end

--- Get preview-colour option from metadata with deprecation support.
--- @param key string The option name to retrieve
--- @param meta table<string, any> Document metadata table
--- @return boolean The option value as a boolean
local function get_preview_colour_option(key, meta)
  -- Check new nested structure: extensions.preview-colour.key
  if not is_empty(meta['extensions']) and
      not is_empty(meta['extensions']['preview-colour']) and
      not is_empty(meta['extensions']['preview-colour'][key]) then
    return meta['extensions']['preview-colour'][key]
  end

  -- Check deprecated top-level structure: preview-colour.key (with warning)
  local deprecated_value = check_deprecated_config(meta, key)
  if deprecated_value ~= nil then
    return deprecated_value
  end

  -- Return default values: code: true, text: false
  if key == 'code' then
    return true
  elseif key == 'text' then
    return false
  end

  return true -- fallback for any other keys
end

--- Convert RGB colour notation to HTML hex format.
--- @param rgb string RGB colour string in format "rgb(r, g, b)"
--- @return string HTML hex colour code in uppercase format (e.g., "#FF0000")
function RGBtoHTML(rgb)
  local r, g, b = rgb:match("rgb%((%d+)%s*,%s*(%d+)%s*,%s*(%d+)%)")
  r = tonumber(r)
  g = tonumber(g)
  b = tonumber(b)
  return string.upper(string.format("#%02x%02x%02x", r, g, b))
end

--- Convert RGB percentage notation to HTML hex format.
--- @param rgb string RGB colour string in format "rgb(r%, g%, b%)"
--- @return string HTML hex colour code in uppercase format (e.g., "#FF0000")
function RGBPercentToHTML(rgb)
  local r, g, b = rgb:match("rgb%((%d+)%s*%%%s*,%s*(%d+)%s*%%%s*,%s*(%d+)%s*%%%s*%)")
  r = math.floor(tonumber(r) * 255 / 100 + 0.5)
  g = math.floor(tonumber(g) * 255 / 100 + 0.5)
  b = math.floor(tonumber(b) * 255 / 100 + 0.5)
  return string.upper(string.format("#%02x%02x%02x", r, g, b))
end

--- Convert HSL colour notation to HTML hex format.
--- @param hsl string HSL colour string in format "hsl(h, s%, l%)"
--- @return string HTML hex colour code in uppercase format (e.g., "#FF0000")
function HSLtoHTML(hsl)
  local h, s, l = hsl:match("hsl%((%d+)%s*,%s*(%d+)%%%s*,%s*(%d+)%%%s*%)")
  h = tonumber(h) / 360
  s = tonumber(s) / 100
  l = tonumber(l) / 100

  --- Helper function to convert hue to RGB component.
  --- @param p number
  --- @param q number
  --- @param t number
  --- @return number RGB component value
  local function hue_to_rgb(p, q, t)
    if t < 0 then t = t + 1 end
    if t > 1 then t = t - 1 end
    if t < 1 / 6 then return p + (q - p) * 6 * t end
    if t < 1 / 2 then return q end
    if t < 2 / 3 then return p + (q - p) * (2 / 3 - t) * 6 end
    return p
  end

  local r, g, b
  if s == 0 then
    r, g, b = l, l, l -- achromatic
  else
    local q = l < 0.5 and l * (1 + s) or l + s - l * s
    local p = 2 * l - q
    r = hue_to_rgb(p, q, h + 1 / 3)
    g = hue_to_rgb(p, q, h)
    b = hue_to_rgb(p, q, h - 1 / 3)
  end

  r = math.floor(r * 255 + 0.5)
  g = math.floor(g * 255 + 0.5)
  b = math.floor(b * 255 + 0.5)

  return string.upper(string.format("#%02x%02x%02x", r, g, b))
end

--- Convert HWB colour notation to HTML hex format.
--- @param hwb string HWB colour string in format "hwb(h w% b%)"
--- @return string HTML hex colour code in uppercase format (e.g., "#FF0000")
function HWBtoHTML(hwb)
  local h, w, b = hwb:match("hwb%((%d+)%s+(%d+)%%%s+(%d+)%%%s*%)")
  h = tonumber(h)
  w = tonumber(w) / 100
  b = tonumber(b) / 100

  -- Normalize whiteness and blackness
  local sum = w + b
  if sum > 1 then
    w = w / sum
    b = b / sum
  end

  -- Convert HWB to RGB
  -- First convert hue to RGB (assuming full saturation and 50% lightness)
  h = h / 360
  --- Helper function to convert hue to RGB component for HWB.
  --- @param p number
  --- @param q number
  --- @param t number
  --- @return number RGB component value
  local function hue_to_rgb(p, q, t)
    if t < 0 then t = t + 1 end
    if t > 1 then t = t - 1 end
    if t < 1 / 6 then return p + (q - p) * 6 * t end
    if t < 1 / 2 then return q end
    if t < 2 / 3 then return p + (q - p) * (2 / 3 - t) * 6 end
    return p
  end

  local r, g, b_color
  local q = 1
  local p = 0
  r = hue_to_rgb(p, q, h + 1 / 3)
  g = hue_to_rgb(p, q, h)
  b_color = hue_to_rgb(p, q, h - 1 / 3)

  -- Apply whiteness and blackness
  r = r * (1 - w - b) + w
  g = g * (1 - w - b) + w
  b_color = b_color * (1 - w - b) + w

  r = math.floor(r * 255 + 0.5)
  g = math.floor(g * 255 + 0.5)
  b_color = math.floor(b_color * 255 + 0.5)

  return string.upper(string.format("#%02x%02x%02x", r, g, b_color))
end

--- Escape special LaTeX characters in text.
--- @param text string The text to escape
--- @return string The escaped text safe for LaTeX
function escape_latex(text)
  -- Escape special LaTeX characters
  -- Note: Order matters - backslash must be escaped first
  text = string.gsub(text, "\\", "\\textbackslash{}")
  text = string.gsub(text, "%{", "\\{")
  text = string.gsub(text, "%}", "\\}")
  text = string.gsub(text, "%$", "\\$")
  text = string.gsub(text, "%&", "\\&")
  text = string.gsub(text, "%%", "\\%%") -- Escape % in replacement string
  text = string.gsub(text, "%#", "\\#")
  text = string.gsub(text, "%^", "\\textasciicircum{}")
  text = string.gsub(text, "%_", "\\_")
  text = string.gsub(text, "~", "\\textasciitilde{}")
  return text
end

--- Escape special Typst characters in text.
--- @param text string The text to escape
--- @return string The escaped text safe for Typst
function escape_typst(text)
  -- Escape special Typst characters
  text = string.gsub(text, "%#", "\\#")
  return text
end

--- Escape special Lua pattern characters for use in string.gsub.
--- @param text string The text containing characters to escape
--- @return string The escaped text safe for Lua patterns
function escape_lua_pattern(text)
  -- Escape special Lua pattern characters for use in string.gsub
  text = string.gsub(text, "%%", "%%%%") -- % must be escaped first
  text = string.gsub(text, "%^", "%%^")
  text = string.gsub(text, "%$", "%%$")
  text = string.gsub(text, "%(", "%%(")
  text = string.gsub(text, "%)", "%%)")
  text = string.gsub(text, "%.", "%%.")
  text = string.gsub(text, "%[", "%%[")
  text = string.gsub(text, "%]", "%%]")
  text = string.gsub(text, "%*", "%%*")
  text = string.gsub(text, "%+", "%%+")
  text = string.gsub(text, "%-", "%%-")
  text = string.gsub(text, "%?", "%%?")
  return text
end

--- Expand 3-character hex colour to 6-character format.
--- @param hex string Hex colour code (either #123 or #123456 format)
--- @return string 6-character hex colour code (e.g., #123 becomes #112233)
function expand_hex_colour(hex)
  -- Convert 3-character hex to 6-character hex (e.g., #123 -> #112233)
  if string.len(hex) == 4 then -- #123 format
    return (string.gsub(hex, "#(%x)(%x)(%x)", "#%1%1%2%2%3%3"))
  end
  return hex -- Already 6-character or other format
end

--- Extract and configure colour preview settings from document metadata.
--- @param meta table<string, any> Document metadata table
--- @return table<string, any> Updated metadata table with preview-colour configuration
function get_colour_preview_meta(meta)
  local preview_colour_text = get_preview_colour_option('text', meta)
  local preview_colour_code = get_preview_colour_option('code', meta)

  meta['extensions']['preview-colour'] = {
    ["text"] = preview_colour_text,
    ["code"] = preview_colour_code
  }
  preview_colour_meta = meta['extensions']['preview-colour']
  return meta
end

--- Extract colour information from a pandoc element.
--- @param element table Pandoc element containing text to analyse
--- @return string|nil hex Extracted hex colour code or nil if no colour found
--- @return string|nil original_colour_text Original colour text that was matched
function get_colour(element)
  --- Generate hex colour pattern for matching.
  --- @param n number Number of hex characters to match
  --- @return string Lua pattern for matching hex colours
  function get_hex_color(n)
    return '#' .. string.rep('[0-9a-fA-F]', n)
  end

  local hex = nil
  local original_colour_text = nil

  for i = 6, 3, -1 do
    hex = element.text:match('(' .. get_hex_color(i) .. ')')
    if (i == 5 or i == 4) and hex ~= nil then
      hex = nil
      break
    end
    if hex ~= nil and (i == 6 or i == 3) then
      original_colour_text = hex
      break
    end
  end
  if hex == nil then
    original_colour_text = element.text:match('(rgb%s*%(%s*%d+%s*,%s*%d+%s*,%s*%d+%s*%))')
    if original_colour_text ~= nil then
      hex = RGBtoHTML(original_colour_text)
    end
  end
  if hex == nil then
    original_colour_text = element.text:match('(rgb%s*%(%s*%d+%s*%%%s*,%s*%d+%s*%%%s*,%s*%d+%s*%%%s*%))')
    if original_colour_text ~= nil then
      hex = RGBPercentToHTML(original_colour_text)
    end
  end
  if hex == nil then
    original_colour_text = element.text:match('(hsl%s*%(%s*%d+%s*,%s*%d+%s*%%,%s*%d+%s*%%s*%))')
    if original_colour_text ~= nil then
      hex = HSLtoHTML(original_colour_text)
    end
  end
  if hex == nil then
    original_colour_text = element.text:match('(hwb%s*%(%s*%d+%s+%d+%%%s+%d+%%%s*%))')
    if original_colour_text ~= nil then
      hex = HWBtoHTML(original_colour_text)
    end
  end

  return hex, original_colour_text
end

--- Create colour preview mark for HTML format.
--- @param hex string Hex colour code
--- @return string HTML colour preview mark
local function create_html_colour_mark(hex)
  return '<span style="display: inline-block; color: ' ..
  hex ..
  '; cursor: pointer; user-select: none; -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; position: relative;" title="Colour preview: ' ..
  hex ..
  ' (click to copy)" aria-label="Colour preview: ' ..
  hex ..
  ' (click to copy)" onclick="navigator.clipboard.writeText(\'' ..
  hex ..
  '\').then(() => { const span = this; const originalTitle = span.title; span.title = \'Copied: ' ..
  hex ..
  '\'; let tooltip = document.createElement(\'div\'); tooltip.textContent = \'Copied!\'; tooltip.style.cssText = \'position:absolute;top:-30px;left:50%;transform:translateX(-50%);background:#333;color:white;padding:4px 8px;border-radius:4px;font-size:12px;font-family:sans-serif;white-space:nowrap;z-index:9999;box-shadow:0 2px 4px rgba(0,0,0,0.3);pointer-events:none;\'; span.appendChild(tooltip); setTimeout(() => { span.title = originalTitle; if (span.contains(tooltip)) span.removeChild(tooltip); }, 1500); }).catch(() => console.error(\'Failed to copy colour code\'));">&#9673;</span>'
end

--- Create colour preview mark for LaTeX format.
--- @param hex string Hex colour code
--- @return string LaTeX colour preview mark
local function create_latex_colour_mark(hex)
  local hex_colour_six = expand_hex_colour(hex)
  return "\\textcolor[HTML]{" .. string.gsub(hex_colour_six, '#', '') .. "}{\\textbullet}"
end

--- Create colour preview mark for Typst format.
--- @param hex string Hex colour code
--- @return string Typst colour preview mark
local function create_typst_colour_mark(hex)
  local hex_colour_six = expand_hex_colour(hex)
  return '#text(fill: rgb("' .. string.lower(hex_colour_six) .. '"))[◉]'
end

--- Create colour preview mark for DOCX format.
--- @param hex string Hex colour code
--- @return string DOCX colour preview mark using OpenXML
local function create_docx_colour_mark(hex)
  local hex_colour_six = expand_hex_colour(hex)
  local hex_without_hash = string.gsub(hex_colour_six, '#', '')
  return '<w:r><w:rPr><w:color w:val="' .. hex_without_hash .. '"/></w:rPr><w:t>●</w:t></w:r>'
end

--- Create colour preview mark for PPTX format.
--- @param hex string Hex colour code
--- @return string PPTX colour preview mark using OpenXML
local function create_pptx_colour_mark(hex)
  local hex_colour_six = expand_hex_colour(hex)
  local hex_without_hash = string.gsub(hex_colour_six, '#', '')
  return '<a:r><a:rPr dirty="0"><a:solidFill><a:srgbClr val="' .. hex_without_hash .. '" /></a:solidFill></a:rPr><a:t>●</a:t></a:r>'
end

--- Get format-specific colour preview mark.
--- @param hex string Hex colour code
--- @return string|nil format Format name (html, latex, typst, openxml) or nil if unsupported
--- @return string|nil mark Colour preview mark for the format or nil if unsupported
local function get_colour_mark_for_format(hex)
  if quarto.doc.is_format("html:js") then
    return "html", create_html_colour_mark(hex)
  elseif quarto.doc.is_format("latex") then
    return "latex", create_latex_colour_mark(hex)
  elseif quarto.doc.is_format("typst") then
    return "typst", create_typst_colour_mark(hex)
  elseif quarto.doc.is_format("docx") then
    return "openxml", create_docx_colour_mark(hex)
  elseif quarto.doc.is_format("pptx") then
    return "openxml", create_pptx_colour_mark(hex)
  end
  return nil, nil
end

--- Process text replacement for string elements with colour previews.
--- @param element table Pandoc element containing text
--- @param hex string Hex colour code
--- @param original_colour_text string Original colour text found in element
--- @param format string Output format name
--- @param colour_mark string Colour preview mark for the format
--- @return table|nil Modified pandoc element or nil
local function process_text_replacement(element, hex, original_colour_text, format, colour_mark)
  -- For OpenXML formats (DOCX/PPTX), we need to return a Span with separate elements
  if format == "openxml" then
    local escaped_pattern = escape_lua_pattern(original_colour_text)
    local escaped_replacement = string.gsub(original_colour_text, "%%", "%%%%")
    local new_text = string.gsub(element.text, escaped_pattern, escaped_replacement)
    return pandoc.Span({
      pandoc.Str(new_text),
      pandoc.RawInline(format, colour_mark)
    })
  end

  -- For other formats (LaTeX, Typst), use the existing concatenation approach
  local escaped_original = original_colour_text
  if format == "latex" then
    escaped_original = escape_latex(original_colour_text)
  elseif format == "typst" then
    escaped_original = escape_typst(original_colour_text)
  end

  local escaped_pattern = escape_lua_pattern(original_colour_text)
  local escaped_colour_mark = string.gsub(colour_mark, "%%", "%%%%")
  local escaped_replacement = string.gsub(escaped_original, "%%", "%%%%") .. escaped_colour_mark
  local new_text = string.gsub(element.text, escaped_pattern, escaped_replacement)

  return pandoc.RawInline(format, new_text)
end

--- Process code element with colour preview.
--- @param element table Pandoc Code element
--- @param format string Output format name
--- @param colour_mark string Colour preview mark for the format
--- @return table Modified pandoc element
local function process_code_element(element, format, colour_mark)
  return pandoc.Span({ element, pandoc.RawInline(format, colour_mark) })
end

--- Process string elements to add colour previews in text.
--- @param element table Pandoc Str element
--- @param meta table<string, any> Document metadata (currently unused)
--- @return table|nil Modified pandoc element with colour preview, or original element
function process_str(element, meta)
  if preview_colour_meta['text'] == false then
    return element
  end

  local hex, original_colour_text = get_colour(element)
  if hex ~= nil and original_colour_text ~= nil then
    local format, colour_mark = get_colour_mark_for_format(hex)
    if format and colour_mark then
      return process_text_replacement(element, hex, original_colour_text, format, colour_mark)
    end
  end
end

--- Process code elements to add colour previews.
--- @param element table Pandoc Code element
--- @return table|nil Modified pandoc element with colour preview, or original element
function process_code(element)
  if preview_colour_meta['code'] == false then
    return element
  end

  local hex, original_colour_text = get_colour(element)
  if hex ~= nil and original_colour_text ~= nil then
    local format, colour_mark = get_colour_mark_for_format(hex)
    if format and colour_mark then
      return process_code_element(element, format, colour_mark)
    end
  end
end

--- Pandoc filter configuration
--- Defines the processing pipeline for different pandoc elements
--- @type table<number, table<string, function>>
return {
  { Meta = get_colour_preview_meta },
  { Str = process_str },
  { Code = process_code }
}
