-- Keep books readable by removing imported wiki/CMS navigation links while
-- retaining citations, source URLs, and genuinely external resources.

local function has_class(element, wanted)
  for _, class in ipairs(element.classes or {}) do
    if class == wanted then return true end
  end
  return false
end

local function is_external(target)
  return target:match('^[A-Za-z][A-Za-z0-9+.-]*:') ~= nil
end

local function is_navigation_url(target)
  local lower = string.lower(target)
  local path = lower:match('^https?://[^/]+(/[^?#]*)') or ''
  local query = lower:match('%?([^#]*)') or ''
  if ('&' .. query .. '&'):find('&action=edit&', 1, true) then return true end
  for _, segment in ipairs({
    'category', 'categories', 'tag', 'tags', 'user', 'users',
    'profile', 'profiles', 'search'
  }) do
    if path == '/' .. segment or path == '/' .. segment .. '/'
        or path:find('/' .. segment .. '/', 1, true) then
      return true
    end
  end
  return false
end

function Link(link)
  local target = link.target or ''
  if has_class(link, 'wikilink') then return link.content end
  if target == '' then return link.content end
  if target:sub(1, 1) == '#' then return nil end
  if not is_external(target) then return link.content end
  if is_navigation_url(target) then return link.content end
  return nil
end
