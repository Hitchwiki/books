-- Consolidated attribution replaces generated Source/License notes after chapters.
-- Some imported wiki pages cite placeholder footnotes whose definitions are empty.
-- Dropping those Note nodes prevents blank numbered entries in every output format.
function Note(note)
  if #note.content == 0 then
    return {}
  end
end

function Para(paragraph)
  local text = pandoc.utils.stringify(paragraph)
  if text:match("^Source:%s") or text:match("^License:%s") then
    return {}
  end
  if text:match("^<references%s*/?>$") then
    return {}
  end
end

function Blocks(blocks)
  local output = {}
  local index = 1
  while index <= #blocks do
    local current = blocks[index]
    local following = blocks[index + 1]
    if current.t == "HorizontalRule"
      and following
      and following.t == "Para"
      and pandoc.utils.stringify(following):match("^Source:%s") then
      index = index + 2
    else
      output[#output + 1] = current
      index = index + 1
    end
  end
  return output
end
