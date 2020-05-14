#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pkgutil

__all__ = []
loaders = []

def get_modules():
	for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
		__all__.append(module_name)
		loaders.append(loader)

def load_modules(names, loaders):
	dependent = []
	dependent_loaders = []
	for i in range(len(names)):
		module_name = names[i]
		loader = loaders[i]
		try:
			_module = loader.find_module(module_name).load_module(module_name)
			globals()[module_name] = _module
			
		except ModuleNotFoundError as e:
			dependent.append(module_name)
			dependent_loaders.append(loader)
			
	for i in range(len(dependent)):
		load_modules(dependent, dependent_loaders)
		
get_modules()
load_modules(__all__, loaders)