#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ChemTools is a collection of interpretive chemical tools for
# analyzing outputs of the quantum chemistry calculations.
#
# Copyright (C) 2016-2019 The ChemTools Development Team
#
# This file is part of ChemTools.
#
# ChemTools is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# ChemTools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --
# pragma pylint: disable=invalid-name
"""Non-Covalent Interactions (NCI) Script."""


from chemtools import Molecule, UniformGrid, NCI


__all__ = ['parse_args_nci', 'main_nci']

# description message
nci_desp = """
Visualize Non-Covalent Interactions (NCI) using VMD package.

The generated files include:
  output.vmd             The VMD script.
  output-dens.cube       The signed density cube file.
  output-grad.cube       The reduced density gradient cube file.

The values of signed density (density multiplied by the sign of 2nd eigenvalue of
Hessian) are multiplied by 100.0 when being recorded in cube file. Similar to NCIPlot
program, this is used for coloring reduced density gradient iso-surface(s).
The values of reduced density gradient are masked using the given denscut argument
before being recorded in cube file. More specifically, similar to NCIPlot program,
the reduced density gradient value of points for which density > denscut will be
set to 100.0 to have VMD only display reduced density gradient iso-surface(s) for
region with density < denscut.

If VMD is setup on your system, you can visualize NCI with the command below:
    $ vmd -e output.vmd
For instruction on how to open the script from the VMD interactive environment,
please refer to ChemTools website.

Note: The output.vmd script requires output-dens.cube & output-grad.cube to plot NCI
      in VMD software (they files should be all in the same directory).
"""


def parse_args_nci(subparser):
    """Parse command-line arguments for computing NCI."""

    # required arguments
    subparser.add_argument(
        'fname',
        help='Wave-function file. Supported formats: fchk, mkl, molden.input, wfn.')

    subparser.add_argument(
        'output', help='Name of generated cube files and vmd script.')

    # optional arguments
    subparser.add_argument(
        '--cube',
        default='0.1,2.0',
        type=str,
        metavar='N',
        help='specify the cubic grid used for visualizing NCI. '
        'This can be either a cube file with .cube extension, or a '
        'user-defined cubic grid specified by spacing and padding parameters '
        'separated by a comma. For example, 0.2,5.0 which specifies 0.2 a.u. '
        'distance between grid points, and 5.0 a.u. extension of cubic grid '
        'on each side of the molecule. This cube is used for evaluating '
        'density, computing reduced density gradient (RDG) and visualizing '
        'NCI using VMD program. [default=%(default)s]')

    subparser.add_argument(
        '--plot',
        default=False,
        action='store_true',
        help='plot reduced density gradient vs. signed density (density'
        'multiplied by sign of hessian\'s 2nd eigenvalue). This generates a '
        'output.png file. This plot is not affected by the value of '
        'denscut argument. [default=%(default)s]')

    subparser.add_argument(
        '--isosurface',
        default=0.5,
        type=float,
        help='iso-surface value of reduced density gradient (RDG) to visualize. '
        '[default=%(default)s]')

    subparser.add_argument(
        '--denscut',
        default=0.05,
        type=float,
        help='density cutoff used in visualizing reduced density gradient (RDG) '
        'iso-surfaces, and dumping reduced density gradient cube file. '
        'Similar to NCIPlot program, reduced density gradient of points with '
        'density > denscut will be set to 100.0 in the corresponding cube '
        'file. This triggers the VMD to only display reduced density gradient '
        'iso-surface(s) in regions for which density < denscut. '
        'For visualizing all reduced density gradient (RDG) iso-surfaces, '
        'disregarding of density value, set this argument to inf or infinity. '
        '[default=%(default)s]')

    subparser.add_argument(
        '--color',
        default='b',
        type=str,
        help='color of reduced density gradient vs. signed density scatter plot'
        ' [default=%(default)s]')


def main_nci(args):
    """Build NCI model and dump VMD script and cube files for visualizing NCI with VMD."""
    # load molecule
    mol = Molecule.from_file(args.fname)

    # make cubic grid
    if args.cube.endswith('.cube'):
        # load cube file
        cube = UniformGrid.from_cube(args.cube)
    elif len(args.cube.split(',')) == 2:
        # make a cubic grid
        spacing, extension = [float(item) for item in args.cube.split(',')]
        cube = UniformGrid.from_molecule(mol, spacing=spacing, extension=extension, rotate=True)
    else:
        raise ValueError('Argument cube={0} is not recognized!'.format(args.cube))

    # build NCI model
    nci = NCI.from_molecule(mol, grid=cube)

    # dump files/scripts for visualizing NCI
    nci.generate_scripts(args.output, isosurf=args.isosurface, denscut=args.denscut)

    # plot reduced density gradient vs. signed density
    if args.plot:
        nci.generate_plot(args.output, color=args.color)
