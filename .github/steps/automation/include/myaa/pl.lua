local DependencyControl = require("l0.DependencyControl")
local version = DependencyControl{
    name = "Penlight",
    version = "1.6.0",
    description = "Python-inspired utility library.",
    author = "stevedonovan",
    url = "http://github.com/Myaamori/Penlight",
    moduleName = "myaa.pl",
}

package.path = package.path .. ";" .. aegisub.decode_path("?user/automation/include/myaa/?.lua")

local modules_to_load = {
    utils = true,path=true,dir=true,tablex=true,stringio=true,sip=true,
    input=true,seq=true,lexer=true,stringx=true,
    config=true,pretty=true,data=true,func=true,text=true,
    operator=true,lapp=true,array2d=true,
    comprehension=true,xml=true,types=true,
    test = true, app = true, file = true, class = true,
    luabalanced = true, permute = true, template = true,
    url = true, compat = true, List = true, Map = true, Set = true,
    OrderedMap = true, MultiMap = true, Date = true,
    -- classes --
}

local modules = {}

for k, v in pairs(modules_to_load) do
    modules[k] = require ("pl." .. k)
end

modules.version = version

return modules
