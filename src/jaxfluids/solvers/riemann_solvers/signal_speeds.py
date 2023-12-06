#*------------------------------------------------------------------------------*
#* JAX-FLUIDS -                                                                 *
#*                                                                              *
#* A fully-differentiable CFD solver for compressible two-phase flows.          *
#* Copyright (C) 2022  Deniz A. Bezgin, Aaron B. Buhendwa, Nikolaus A. Adams    *
#*                                                                              *
#* This program is free software: you can redistribute it and/or modify         *
#* it under the terms of the GNU General Public License as published by         *
#* the Free Software Foundation, either version 3 of the License, or            *
#* (at your option) any later version.                                          *
#*                                                                              *
#* This program is distributed in the hope that it will be useful,              *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of               *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                *
#* GNU General Public License for more details.                                 *
#*                                                                              *
#* You should have received a copy of the GNU General Public License            *
#* along with this program.  If not, see <https://www.gnu.org/licenses/>.       *
#*                                                                              *
#*------------------------------------------------------------------------------*
#*                                                                              *
#* CONTACT                                                                      *
#*                                                                              *
#* deniz.bezgin@tum.de // aaron.buhendwa@tum.de // nikolaus.adams@tum.de        *
#*                                                                              *
#*------------------------------------------------------------------------------*
#*                                                                              *
#* Munich, April 15th, 2022                                                     *
#*                                                                              *
#*------------------------------------------------------------------------------*

from typing import Tuple

import jax.numpy as jnp 

def signal_speed_Arithmetic(u_L: jax.Array, u_R: jax.Array, a_L: jax.Array, a_R: jax.Array,
    *args, **kwargs) -> Tuple[jax.Array, jax.Array]:
    """Arithmetic signal speed estimate

    :param u_L: Buffer with normal velocity in left neighboring cell.
    :type u_L: jax.Array
    :param u_R: Buffer with normal velocity in right neighboring cell.
    :type u_R: jax.Array
    :param a_L: Buffer with speed of sound in left neighboring cell.
    :type a_L: jax.Array
    :param a_R: Buffer with speed of sound in right neighboring cell.
    :type a_R: jax.Array
    :return: Buffers of left and right going wave speed estimates.
    :rtype: Tuple[jax.Array, jax.Array]
    """
    u_mean = 0.5 * (u_L + u_R)
    a_mean = 0.5 * (a_L + a_R)
    S_L = jnp.minimum(u_mean - a_mean, u_L - a_L)
    S_R = jnp.maximum(u_mean + a_mean, u_R + a_R)
    return S_L, S_R

def signal_speed_Rusanov(u_L: jax.Array, u_R: jax.Array, a_L: jax.Array, a_R: jax.Array,
    *args, **kwargs) -> Tuple[jax.Array, jax.Array]:
    """Rusanov type signal speed estimate

    :param u_L: Buffer with normal velocity in left neighboring cell.
    :type u_L: jax.Array
    :param u_R: Buffer with normal velocity in right neighboring cell.
    :type u_R: jax.Array
    :param a_L: Buffer with speed of sound in left neighboring cell.
    :type a_L: jax.Array
    :param a_R: Buffer with speed of sound in right neighboring cell.
    :type a_R: jax.Array
    :return: Buffers of left and right going wave speed estimates.
    :rtype: Tuple[jax.Array, jax.Array]
    """
    S_plus = jnp.maximum(jnp.abs(u_L) + a_L, jnp.abs(u_R) + a_R)
    S_L = - S_plus
    S_R = S_plus
    return S_L, S_R

def signal_speed_Davis(u_L: jax.Array, u_R: jax.Array, a_L: jax.Array, a_R: jax.Array,
    *args, **kwargs) -> Tuple[jax.Array, jax.Array]:
    """Davis signal speed estimate
    See Toro Eq. (10.48)

    :param u_L: Buffer with normal velocity in left neighboring cell.
    :type u_L: jax.Array
    :param u_R: Buffer with normal velocity in right neighboring cell.
    :type u_R: jax.Array
    :param a_L: Buffer with speed of sound in left neighboring cell.
    :type a_L: jax.Array
    :param a_R: Buffer with speed of sound in right neighboring cell.
    :type a_R: jax.Array
    :return: Buffers of left and right going wave speed estimates.
    :rtype: Tuple[jax.Array, jax.Array]
    """
    S_L = jnp.minimum( u_L - a_L, u_R - a_R )
    S_R = jnp.maximum( u_L + a_L, u_R + a_R )
    return S_L, S_R

def signal_speed_Davis_2(u_L: jax.Array, u_R: jax.Array, a_L: jax.Array, a_R: jax.Array,
    rho_L: jax.Array, rho_R: jax.Array, H_L: jax.Array, H_R: jax.Array, gamma: float,
    *args, **kwargs) -> Tuple[jax.Array, jax.Array]:
    """Signal speed estimate according to Davis.

    :param u_L: Buffer with normal velocity in left neighboring cell.
    :type u_L: jax.Array
    :param u_R: Buffer with normal velocity in right neighboring cell.
    :type u_R: jax.Array
    :param a_L: Buffer with speed of sound in left neighboring cell.
    :type a_L: jax.Array
    :param a_R: Buffer with speed of sound in right neighboring cell.
    :type a_R: jax.Array
    :param rho_L: Buffer with densitites in left neighboring cell.
    :type rho_L: jax.Array
    :param rho_R: Buffer with densitites in right neighboring cell.
    :type rho_R: jax.Array
    :param H_L: Buffer with total enthalpies in left neighboring cell.
    :type H_L: jax.Array
    :param H_R: Buffer with enthalpies in right neighboring cell.
    :type H_R: jax.Array
    :param gamma: Ratio of specific heats.
    :type gamma: float
    :return: Buffers of left and right going wave speed estimates.
    :rtype: Tuple[jax.Array, jax.Array]
    """

    one_dens = 1.0 / (jnp.sqrt(rho_L) + jnp.sqrt(rho_R))
    u_Roe = ( jnp.sqrt(rho_L) * u_L + jnp.sqrt(rho_R) * u_R ) * one_dens
    H_Roe = ( jnp.sqrt(rho_L) * H_L + jnp.sqrt(rho_R) * H_R ) * one_dens
    a_Roe = jnp.sqrt( (gamma - 1) * (H_Roe - 0.5 * u_Roe * u_Roe) )
    S_L = u_Roe - a_Roe
    S_R = u_Roe + a_Roe
    return S_L, S_R

def signal_speed_Einfeldt(u_L: jax.Array, u_R: jax.Array, a_L: jax.Array, a_R: jax.Array,
    rho_L: jax.Array, rho_R: jax.Array, *args, **kwargs) -> Tuple[jax.Array, jax.Array]:
    """Einfeldt signal speed estimate
    See Toro Eqs. (10.52) - (10.54) 

    :param u_L: Buffer with normal velocity in left neighboring cell.
    :type u_L: jax.Array
    :param u_R: Buffer with normal velocity in right neighboring cell.
    :type u_R: jax.Array
    :param a_L: Buffer with speed of sound in left neighboring cell.
    :type a_L: jax.Array
    :param a_R: Buffer with speed of sound in right neighboring cell.
    :type a_R: jax.Array
    :return: Buffers of left and right going wave speed estimates.
    :rtype: Tuple[jax.Array, jax.Array]
    """
    one_dens = 1.0 / (jnp.sqrt(rho_L) + jnp.sqrt(rho_R))
    eta2 = 0.5 * jnp.sqrt(rho_L) * jnp.sqrt(rho_R) * one_dens * one_dens
    u_bar = ( jnp.sqrt(rho_L) * u_L + jnp.sqrt(rho_R) * u_R ) * one_dens
    d_bar = jnp.sqrt( ( jnp.sqrt(rho_L) * a_L * a_L + jnp.sqrt(rho_R) * a_R * a_R ) * one_dens + eta2 * (u_R - u_L) * (u_R - u_L) )
    S_L = u_bar - d_bar
    S_R = u_bar + d_bar
    return S_L, S_R

def signal_speed_Toro(u_L: jax.Array, u_R: jax.Array, a_L: jax.Array, a_R: jax.Array,
    rho_L: jax.Array, rho_R: jax.Array, p_L: jax.Array, p_R: jax.Array, gamma: float, 
    *args, **kwargs) -> Tuple[jax.Array, jax.Array]:
    """Toro signal speed estimate
    See Toro Eqs. (10.59) - (10.60) 

    :param u_L: Buffer with normal velocity in left neighboring cell.
    :type u_L: jax.Array
    :param u_R: Buffer with normal velocity in right neighboring cell.
    :type u_R: jax.Array
    :param a_L: Buffer with speed of sound in left neighboring cell.
    :type a_L: jax.Array
    :param a_R: Buffer with speed of sound in right neighboring cell.
    :type a_R: jax.Array
    :rtype: Tuple[jax.Array, jax.Array]
    """
    p_star = estimate_pressure(u_L, u_R, a_L, a_R, rho_L, rho_R, p_L, p_R)
    gamma_ = (gamma + 1) * 0.5 / gamma
    q_L = 1.0 * (p_star <= p_L) + jnp.sqrt( 1 + gamma_ * (p_star / p_L - 1) ) * (p_star > p_L)
    q_R = 1.0 * (p_star <= p_R) + jnp.sqrt( 1 + gamma_ * (p_star / p_R - 1) ) * (p_star > p_R)
    S_L = u_L - a_L * q_L
    S_R = u_R + a_R * q_R
    return S_L, S_R

def compute_sstar(u_L: jax.Array, u_R: jax.Array, p_L: jax.Array, p_R: jax.Array, 
    rho_L: jax.Array, rho_R: jax.Array, S_L: jax.Array, S_R: jax.Array) -> jax.Array:
    """Computes the speed of the intermediate wave in a Riemann problem.

    See Toro Eq. (10.70)

    :param u_L: Buffer with normal velocity in left neighboring cell.
    :type u_L: jax.Array
    :param u_R: Buffer with normal velocity in right neighboring cell.
    :type u_R: jax.Array
    :param p_L: Pressure of left neighboring cell.
    :type p_L: jax.Array
    :param p_R: Pressure of right neighboring cells.
    :type p_R: jax.Array
    :param rho_L: Density of left neighboring cell.
    :type rho_L: jax.Array
    :param rho_R: Density of right neighboring cell.
    :type rho_R: jax.Array
    :param S_L: Wave speed estimate left-going wave.
    :type S_L: jax.Array
    :param S_R: Wave speed estimate right-going wave.
    :type S_R: jax.Array
    :return: Speed of the intermediate wave in the Riemann problem.
    :rtype: jax.Array
    """

    delta_uL = S_L - u_L
    delta_uR = S_R - u_R
    rho_deltaSU = rho_L * delta_uL - rho_R * delta_uR
    S_star = 1.0 / rho_deltaSU * (p_R - p_L + rho_L * u_L * delta_uL - rho_R * u_R * delta_uR)
    return S_star

def estimate_pressure(u_L: jax.Array, u_R: jax.Array, a_L: jax.Array, a_R: jax.Array, 
    rho_L: jax.Array, rho_R: jax.Array, p_L: jax.Array, p_R: jax.Array) -> jax.Array:
    """Estimates the pressure in the star region based on a 
    linearised solution in terms of primitive variables. 

    See Toro Eq. (9.28) or (10.67)

    :param u_L: Buffer with normal velocity in left neighboring cell.
    :type u_L: jax.Array
    :param u_R: Buffer with normal velocity in right neighboring cell.
    :type u_R: jax.Array
    :param a_L: Buffer with speed of sound in left neighboring cell.
    :type a_L: jax.Array
    :param a_R: Buffer with speed of sound in right neighboring cell.
    :type a_R: jax.Array
    :param rho_L: Densities of left neighboring cells.
    :type rho_L: jax.Array
    :param rho_R: Densities of right neighboring cells.
    :type rho_R: jax.Array
    :param p_L: Pressure of left neighboring cell.
    :type p_L: jax.Array
    :param p_R: Pressure of right neighboring cells.
    :type p_R: jax.Array
    :return: Pressure in the star region.
    :rtype: jax.Array
    """
    rho_bar = 0.5 * (rho_L + rho_R)
    a_bar = 0.5 * (a_L + a_R)
    p_pvrs = 0.5 * (p_L + p_R) - 0.5 * (u_R - u_L) * rho_bar * a_bar
    p_star = jnp.maximum(0.0, p_pvrs)
    return p_star