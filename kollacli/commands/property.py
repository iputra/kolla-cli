# Copyright(c) 2015, Oracle and/or its affiliates.  All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import traceback

import kollacli.i18n as u

from kollacli.common import properties
from kollacli.common import utils
from kollacli.exceptions import CommandError

from cliff.command import Command
from cliff.lister import Lister


def _get_names(args_list):
    csv_list = args_list[0].strip()
    names = utils.convert_to_unicode(csv_list).split(',')
    if 'all' in names:
        names = None
    return names


class PropertySet(Command):
    "Property Set"

    def get_parser(self, prog_name):
        parser = super(PropertySet, self).get_parser(prog_name)
        parser.add_argument('propertyname', metavar='<propertyname>',
                            help=u._('Property name'))
        parser.add_argument('propertyvalue', metavar='<propertyvalue',
                            help=u._('Property value'))
        parser.add_argument('--hosts', nargs=1,
                            metavar='<host_list>',
                            help=u._('Property host list'))
        parser.add_argument('--groups', nargs=1,
                            metavar='<group_list>',
                            help=u._('Property group list'))
        return parser

    def take_action(self, parsed_args):
        try:
            property_name = parsed_args.propertyname.strip()
            property_value = parsed_args.propertyvalue.strip()

            if parsed_args.hosts:
                if parsed_args.groups:
                    raise CommandError(
                        u._('Invalid to use both hosts and groups arguments ' +
                            'together.'))

                host_names = _get_names(parsed_args.hosts)
                ansible_properties = \
                    properties.AnsibleProperties(load_globals=False,
                                                 load_groups=False,
                                                 load_hosts=True)
                ansible_properties.set_host_property(property_name,
                                                     property_value,
                                                     host_names)

            elif parsed_args.groups:
                group_names = _get_names(parsed_args.groups)
                ansible_properties = \
                    properties.AnsibleProperties(load_globals=False,
                                                 load_groups=True,
                                                 load_hosts=False)
                ansible_properties.set_group_property(property_name,
                                                      property_value,
                                                      group_names)
            else:
                ansible_properties = \
                    properties.AnsibleProperties(load_globals=True,
                                                 load_groups=False,
                                                 load_hosts=False)
                ansible_properties.set_property(property_name,
                                                property_value)

        except Exception:
            raise Exception(traceback.format_exc())


class PropertyClear(Command):
    "Property Clear"

    def get_parser(self, prog_name):
        parser = super(PropertyClear, self).get_parser(prog_name)
        parser.add_argument('propertyname', metavar='<propertyname>',
                            help=u._('Property name'))
        parser.add_argument('--hosts', nargs=1,
                            metavar='<host_list>',
                            help=u._('Property host list'))
        parser.add_argument('--groups', nargs=1,
                            metavar='<group_list>',
                            help=u._('Property group list'))
        return parser

    def take_action(self, parsed_args):
        try:
            property_name = parsed_args.propertyname.strip()

            if parsed_args.hosts:
                if parsed_args.groups:
                    raise CommandError(
                        u._('Invalid to use both hosts and groups arguments ' +
                            'together.'))

                host_names = _get_names(parsed_args.hosts)
                ansible_properties = \
                    properties.AnsibleProperties(load_globals=False,
                                                 load_groups=False,
                                                 load_hosts=True)
                ansible_properties.clear_host_property(property_name,
                                                       host_names)

            elif parsed_args.groups:
                group_names = _get_names(parsed_args.groups)
                ansible_properties = \
                    properties.AnsibleProperties(load_globals=False,
                                                 load_groups=True,
                                                 load_hosts=False)
                ansible_properties.clear_group_property(property_name,
                                                        group_names)

            else:
                ansible_properties = \
                    properties.AnsibleProperties(load_globals=True,
                                                 load_groups=False,
                                                 load_hosts=False)
                ansible_properties.clear_property(property_name)

        except Exception:
            raise Exception(traceback.format_exc())


class PropertyList(Lister):
    """List all properties"""

    def __init__(self, app, app_args, cmd_name=None):
        super(Lister, self).__init__(app, app_args,
                                     cmd_name=cmd_name)

        self.is_global = True
        self.is_all_flag = False
        self.is_long_flag = False
        self.list_type = None

    def get_parser(self, prog_name):
        parser = super(PropertyList, self).get_parser(prog_name)
        parser.add_argument('--all', action='store_true',
                            help=u._('List all properties'))
        parser.add_argument('--long', action='store_true',
                            help=u._('Show all property attributes'))
        parser.add_argument('--hosts', nargs=1,
                            metavar='<host_list>',
                            help=u._('Property host list'))
        parser.add_argument('--groups', nargs=1,
                            metavar='<group_list>',
                            help=u._('Property group list'))
        return parser

    def take_action(self, parsed_args):
        try:
            if parsed_args.all:
                self.is_all_flag = True
            if parsed_args.long:
                self.is_long_flag = True

            if parsed_args.hosts:
                if parsed_args.groups:
                    raise CommandError(
                        u._('Invalid to use both hosts and groups arguments '
                            'together.'))

                self.is_global = False
                self.list_type = u._('Host')
                host_names = _get_names(parsed_args.hosts)

                ansible_properties = \
                    properties.AnsibleProperties(load_globals=False,
                                                 load_groups=False,
                                                 load_hosts=True)
                property_list = \
                    ansible_properties.get_host_list(host_names)

            elif parsed_args.groups:
                self.is_global = False
                self.list_type = u._('Group')
                group_names = _get_names(parsed_args.groups)
                ansible_properties = \
                    properties.AnsibleProperties(load_globals=False,
                                                 load_groups=True,
                                                 load_hosts=False)
                property_list = \
                    ansible_properties.get_group_list(group_names)

            else:
                ansible_properties = \
                    properties.AnsibleProperties(load_globals=True,
                                                 load_groups=False,
                                                 load_hosts=False)

                property_list = ansible_properties.get_all_unique()

            data = self._get_list_data(property_list)
            header = self._get_list_header()
            return (header, data)

        except Exception:
            raise Exception(traceback.format_exc())

    def _get_list_header(self):
        header = None
        if self.is_long_flag:
            if self.is_global:
                header = (u._('Property Name'), u._('Property Value'),
                          u._('Overrides'), u._('Original Value'))
            else:
                header = (u._('Property Name'), u._('Property Value'),
                          u._('Overrides'), u._('Original Value'),
                          self.list_type)
        else:
            if self.is_global:
                header = (u._('Property Name'), u._('Property Value'))
            else:
                header = (u._('Property Name'), u._('Property Value'),
                          self.list_type)
        return header

    def _get_list_data(self, property_list):
        data = []
        if property_list:
            property_length = utils.get_property_list_length()
            for prop in property_list:
                include_prop = False
                if (prop.value is not None and
                        len(str(prop.value)) > property_length):
                    if self.is_all_flag:
                        include_prop = True
                else:
                    include_prop = True

                if not include_prop:
                    continue

                if self.is_long_flag:
                    if self.is_global:
                        data.append((prop.name, prop.value,
                                     prop.overrides,
                                     prop.orig_value))
                    else:
                        data.append((prop.name, prop.value,
                                     prop.overrides,
                                     prop.orig_value, prop.target))
                else:
                    if self.is_global:
                        data.append((prop.name, prop.value))
                    else:
                        data.append((prop.name, prop.value,
                                     prop.target))
        else:
            if self.is_long_flag:
                if self.is_global:
                    data.append(('', '', '', ''))
                else:
                    data.append(('', '', '', '', ''))
            else:
                if self.is_global:
                    data.append(('', ''))
                else:
                    data.append(('', '', ''))

        return data