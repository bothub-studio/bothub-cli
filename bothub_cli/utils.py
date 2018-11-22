# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import re
import sys
import time
from datetime import datetime
from datetime import timedelta
import yaml
import requests
import tarfile
import pathspec
import json
import shutil
from ruamel.yaml import YAML

from bothub_cli import __version__
from bothub_client import __version__ as sdk_version
from bothub_cli import exceptions as exc
from bothub_cli import template

PYPI_VERSION_PATTERN = re.compile(r'bothub_cli-(.+?)-py2.py3-none-any.whl')
PYPI_VERSION_PATTERN_SDK = re.compile(r'bothub-(.+?)-py2.py3-none-any.whl')
PACKAGE_IGNORE_PATTERN = [
    re.compile('.bothub-meta'),
    re.compile('dist'),
    re.compile('.*\.pyc'),
    re.compile('.*/__pycache__/.*'),
]


class Cache(object):
    def __init__(self, path=None):
        self.cache_path = path or os.path.expanduser(os.path.join('~', '.bothub', 'caches.yml'))
        parent_path = os.path.dirname(self.cache_path)
        if not os.path.isdir(parent_path):
            os.makedirs(parent_path)

    def get(self, key):
        if not os.path.isfile(self.cache_path):
            return None
        content = read_content_from_file(self.cache_path)
        cache_entry = yaml.load(content)
        if not cache_entry or not (key in cache_entry):
            return None
        entry = cache_entry[key]
        now = datetime.now()
        if now > entry['expires']:
            return None
        return entry['value']

    def set(self, key, value, ttl=3600):
        if not os.path.isfile(self.cache_path):
            cache_obj = {}
        else:
            content = read_content_from_file(self.cache_path)
            cache_obj = yaml.load(content)
            if not cache_obj:
                cache_obj = {}
        cache_entry = cache_obj.setdefault(key, {})
        cache_entry['value'] = value
        cache_entry['expires'] = datetime.now() + timedelta(seconds=ttl)
        write_content_to_file(self.cache_path, yaml.dump(cache_obj, default_flow_style=False))


def safe_mkdir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def write_content_to_file(path, content):
    with open(path, 'w') as fout:
        fout.write(content)


def read_content_from_file(path):
    if os.path.isfile(path):
        with open(path) as fin:
            return fin.read()


def find_versions(content, sdk=False):
    if sdk: return set(PYPI_VERSION_PATTERN_SDK.findall(content))
    return set(PYPI_VERSION_PATTERN.findall(content))


def cmp_versions(a, b):
    version_a = tuple([int(e) for e in a.split('.')])
    version_b = tuple([int(e) for e in b.split('.')])

    if version_a > version_b:
        return 1
    if version_a < version_b:
        return -1
    return 0


def get_latest_version(versions):
    sorted_versions = sorted(versions, key=lambda v: tuple([int(e) for e in v.split('.')]), reverse=True)
    return sorted_versions[0]


def get_latest_version_from_pypi(use_cache=True, cache=None, sdk=False):
    catch_label = 'latest_pypi_version'
    url = 'https://pypi.python.org/simple/bothub-cli'
    if sdk:
        catch_label = 'sdk_latest_pypi_version'
        url = 'https://pypi.python.org/simple/bothub'

    try:
        if use_cache:
            _cache = cache or Cache()
            latest_version = _cache.get(catch_label)
            if latest_version:
                return latest_version

        response = requests.get(url, timeout=2)
        content = response.content.decode('utf8')
        versions = find_versions(content, sdk)
        latest_version = get_latest_version(versions)
        if use_cache:
            _cache.set(catch_label, latest_version)
        return latest_version
    except requests.exceptions.Timeout:
        raise exc.Timeout()


def check_latest_version():
    try:
        pypi_version = get_latest_version_from_pypi()
        is_latest = cmp_versions(__version__, pypi_version) >= 0
        if not is_latest:
            raise exc.NotLatestVersion(__version__, pypi_version)

    except exc.Timeout:
        pass

def check_latest_version_sdk():
    try:
        pypi_version = get_latest_version_from_pypi(sdk=True)
        is_latest = cmp_versions(sdk_version, pypi_version) >= 0
        if not is_latest:
            raise exc.NotLatestVersionSdk(sdk_version, pypi_version)

    except exc.Timeout:
        pass

def timestamp(dt=None):
    dt = dt or datetime.utcnow()
    return int(time.mktime(dt.timetuple()))


def check_ignore_pattern(name):
    for pattern in PACKAGE_IGNORE_PATTERN:
        if pattern.match(name):
            raise exc.IgnorePatternMatched()


def make_dist_package(dist_file_path, source_dir='.', ignores=None):
    '''Make dist package file of current project directory.
    Includes all files of current dir, bothub dir and tests dir.
    Dist file is compressed with tar+gzip.'''
    if os.path.isfile(dist_file_path):
        os.remove(dist_file_path)

    if ignores:
        with open('.bothubignore', 'r') as fh:
            spec = pathspec.PathSpec.from_lines('gitignore', fh)
            
        with tarfile.open(dist_file_path, 'w:gz') as tout:
            for dirname, dirnames, filenames in os.walk(source_dir):
                for filename in filenames:
                    file = os.path.join(dirname, filename)
                    if not spec.match_file(file):
                        tout.add(file)
    else:
        with tarfile.open(dist_file_path, 'w:gz') as tout:
            for fname in os.listdir(source_dir):
                try:
                    check_ignore_pattern(fname)
                    if os.path.isfile(fname):
                        tout.add(fname)
                    elif os.path.isdir(fname):
                        tout.add(fname)
                except exc.IgnorePatternMatched:
                    pass


def extract_dist_package(dist_file_path, target_dir=None):
    '''Extract dist package file to current directory.'''
    _target_dir = target_dir or '.'

    with tarfile.open(dist_file_path, 'r:gz') as tin:
        tin.extractall(_target_dir)


def make_event(message):
    '''Make dummy event for test mode.'''
    data = {
        'trigger': 'cli',
        'channel': 'cli',
        'sender': {
            'id': 'localuser',
            'name': 'Local user'
        },
        'raw_data': message
    }

    if message.startswith('/location'):
        _, latitude, longitude = message.split()
        data['location'] = {
            'latitude': latitude,
            'longitude': longitude
        }
    elif message:
        data['content'] = message

    return data


def tabulate_dict(lst, *fields):
    result = [None] * len(lst)
    for row_idx, row in enumerate(lst):
        row_result = [None] * len(fields)
        for col_idx, field in enumerate(fields):
            row_result[col_idx] = row[field]
        result[row_idx] = row_result
    return result


def get_bot_class(target_dir='.'):
    try:
        sys.path.append(target_dir)
        __import__('bothub.bot')
        mod = sys.modules['bothub.bot']
        return mod.Bot
    except ImportError:
        if sys.exc_info()[-1].tb_next:
            raise
        else:
            raise exc.ModuleLoadException()


def make_intents_json(agent_folder, display_name, target_dic, lang):
    intents_path = os.path.join(agent_folder, "intents")
    intent_info_dic = {}
    intent_usersays_dic = {}
    join_info = {}
    join_usersays = []
    
    for key, value in target_dic.items():
        if key != "training_phrases":
            intent_info_dic[key] = value
        else:
            intent_usersays_dic[key] = value

    join_info = joining_info_func(template.intent_info, intent_info_dic)
    with open(os.path.join(intents_path, display_name) + ".json", "w", encoding='utf-8') as f:
        json.dump(join_info, f, indent=4, ensure_ascii=False)
    if "training_phrases" in intent_usersays_dic:
        join_usersays = joining_usersays_func(intent_usersays_dic)
        with open(os.path.join(intents_path, display_name) + "_usersays_" + lang + ".json", "w", encoding='utf-8') as f:
            json.dump(join_usersays, f, indent=4, ensure_ascii=False)


def make_entities_json(agent_folder, display_name, target_list, lang):
    entities_path = os.path.join(agent_folder, "entities")
    join_info = {}
    join_entries = []

    join_info = template.entity_info.copy()
    join_info["name"] = display_name
    join_entries = target_list["data"]

    with open(os.path.join(entities_path, display_name) + ".json", "w", encoding='utf-8') as f:
        json.dump(join_info, f, indent=4, ensure_ascii=False)
    with open(os.path.join(entities_path, display_name) + "_entries_" + lang + ".json", "w", encoding='utf-8') as f:
        json.dump(join_entries, f, indent=4, ensure_ascii=False)


def make_etc_json(agent_folder):
    with open(os.path.join(agent_folder, "agent.yml"), "r") as agent_yml_file:
        agent_json = yaml.load(agent_yml_file)
    with open(os.path.join(agent_folder, "agent.json"), "w", encoding='utf-8') as f:
        json.dump(agent_json, f, indent=4, ensure_ascii=False)
    with open(os.path.join(agent_folder, "package.yml"), "r") as package_yml_file:
        package_json = yaml.load(package_yml_file)
    with open(os.path.join(agent_folder, "package.json"), "w", encoding='utf-8') as f:
        json.dump(package_json, f, indent=4, ensure_ascii=False)


def make_intents_yml(agent_folder, lang):
    path = os.path.join(agent_folder, "intents")
    intent_dic = {}

    for f in os.listdir(path):
        if "usersays" in f:
            continue
        filtered_info = {}
        filtered_phrases = {}
        contents = {}
        intent_name = f.replace(".json", "")
        pair_file = f.replace(".json", "_usersays_" + lang + ".json")

        file_path = os.path.join(path, f)
        filtered_info = filter_intent_info(file_path)
        contents.update(filtered_info)

        if os.path.exists(os.path.join(path, pair_file)):
            file_path = os.path.join(path, pair_file)
            filtered_phrases = filter_intent_usersays(file_path)
            contents.update(filtered_phrases)
        intent_dic[intent_name] = contents

    with open(os.path.join(agent_folder, 'intents.yml'), 'w') as yaml_file:
        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(intent_dic, yaml_file)


def make_entities_yml(agent_folder, lang):
    path = os.path.join(agent_folder, "entities")
    try:
        entity_dic = {}
        for f in os.listdir(path):
            if "entries" in f:
                continue
            entity_name = f.replace(".json", "")
            pair_file = f.replace(".json", "_entries_" + lang + ".json")

            file_path1 = os.path.join(path, f)
            with open(file_path1) as json_file1:
                json_obj = json.load(json_file1)
                filtered_obj = filtering_info(json_obj, template.entity_info)

            file_path2 = os.path.join(path, pair_file)
            with open(file_path2) as json_file2:
                json_obj = json.load(json_file2)
                filtered_obj["data"] = json_obj
            entity_dic[entity_name] = filtered_obj
    except FileNotFoundError:
        entity_dic = template.entity_yaml

    with open(os.path.join(agent_folder, 'entities.yml'), 'w') as yaml_file:
        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(entity_dic, yaml_file)


def make_etc_yml(agent_folder):
    agent_file = os.path.join(agent_folder, "agent.json")
    package_file = os.path.join(agent_folder, "package.json")

    with open(agent_file) as f1:
        agent_dic = json.load(f1)
    with open(os.path.join(agent_folder, 'agent.yml'), 'w') as yaml_file:
        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(agent_dic, yaml_file)

    with open(package_file) as f2:
        package_dic = json.load(f2)
    with open(os.path.join(agent_folder, 'package.yml'), 'w') as yaml_file:
        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(package_dic, yaml_file)

    
def filter_intent_usersays(file_path):
    target_json = {}
    with open(file_path) as json_file:
        target_json = json.load(json_file)

    result_dict = {"training_phrases":[]}
    for item in target_json:
        filtered_info = filtering_info(item, template.intent_usersays)
        full_text = ""
        phrase = {}
        phrase_part = []

        for data in filtered_info["data"]:
            text = data["text"]
            full_text += text
            try:
                meta = data["meta"]
                phrase_part.append({text:meta})
            except:
                phrase_part.append(text)
                continue
        if len(phrase_part) == 1:
            phrase = full_text
        else:
            phrase = {full_text:phrase_part}
        result_dict["training_phrases"].append(phrase)
    return result_dict


def filter_intent_info(file_path):
    target_json = {}
    with open(file_path) as json_file:
        target_json = json.load(json_file)
    result = filtering_info(target_json, template.intent_info)
    return result

        
def filtering_info(target_json_obj, default_json_obj):
    result = {}
    for key, value in target_json_obj.items():
        try:
            if key == "id":
                continue
            default_value = default_json_obj[key]
        except KeyError:
            if not value and not isinstance(value, bool):
                continue
            result[key] = value
            continue

        if isinstance(value, dict):
            value = filtering_info(value, default_value)
            if not value:
                continue
        elif isinstance(value, list):
            if len(value) == 0:
                continue
            elif isinstance(value[0], dict):
                result_list = []
                if len(default_value) == 0:
                    default_item = {}
                else:
                    default_item = default_value[0]
                for item in value:
                    value = filtering_info(item, default_item)
                    if not value  and not isinstance(value, bool):
                        continue
                    result_list.append(value)
                if len(result_list) is 0:
                    continue
                value = result_list
        elif value == default_value:
            continue
        result[key] = value
    return result


def joining_info_func(default_obj, target_obj):
    join_obj = {}
    for key, value in default_obj.items():
        if key in target_obj:
            if isinstance(value, str):
                if target_obj[key]:
                    value = target_obj[key]
            elif isinstance(value, list):
                if len(value) == 0:
                    if len(target_obj[key]) == 0:
                        join_obj[key] = value
                        continue
                    else:
                        value = target_obj[key]        
                else:
                    obj_list = []
                    for obj in target_obj[key]:
                        obj_list.append(joining_info_func(value[0], obj))
                    value = obj_list
            elif isinstance(value, dict):
                value = joining_info_func(value, target_obj[key])
        join_obj[key] = value
    return join_obj


def joining_usersays_func(usersays_dic):
    usersays_list = []
    for usersay in usersays_dic["training_phrases"]:
        data_list = []
        if isinstance(usersay, dict):
            part = list(usersay.values())[0]
            for item in part:
                data = {}
                if isinstance(item, str):
                    data = {
                        "text" : item,
                        "userDefined" : False
                    }
                elif isinstance(item, dict):
                    text_info = list(item.items())[0]
                    text = text_info[0]
                    entity = text_info[1]
                    data = {
                        "text" : text,
                        "alias" : entity[1:],
                        "meta" : entity,
                        "userDefined" : True
                    }
                data_list.append(data)
        elif isinstance(usersay, str):
            data = {
                    "text" : usersay,
                    "userDefined" : False
                }
            data_list.append(data)
        usersays = template.intent_usersays.copy()
        usersays["data"] = data_list
        usersays_list.append(usersays)

    return usersays_list