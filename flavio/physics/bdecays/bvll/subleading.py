import flavio
import numpy as np
from flavio.classes import AuxiliaryQuantity, Implementation
from flavio.physics.bdecays.common import meson_quark
from flavio.physics.bdecays.wilsoncoefficients import wctot_dict
from flavio.physics.common import conjugate_par, conjugate_wc, add_dict
from flavio.config import config

r"""Functions to parametrize subleading hadronic effects in $B\to V\ell^+\ell^-$
decays."""


# First, we define functions that allow us to get a contribution to the
# amplitudes from an effective, helicity dependent shift in either C7 or C9

# auxiliary function to construct helicity_amps_deltaC7, helicity_amps_deltaC9
def _helicity_amps_deltaC(q2, deltaC, C_name, par, B, V, lep):
    ml = par['m_'+lep]
    mB = par['m_'+B]
    mV = par['m_'+V]
    scale = config['renormalization scale']['bvll']
    mb = flavio.physics.running.running.get_mb(par, scale)
    N = flavio.physics.bdecays.bvll.amplitudes.prefactor(q2, par, B, V, lep)
    ff = flavio.physics.bdecays.bvll.amplitudes.get_ff(q2, par, B, V)
    wc  = {'7': 0, '7p': 0, 'v': 0, 'a': 0, 's': 0, 'p': 0, 't': 0,'vp': 0, 'ap': 0, 'sp': 0, 'pp': 0, 'tp': 0, }
    wc[C_name] = deltaC
    return flavio.physics.bdecays.angular.helicity_amps_v(q2, mB, mV, mb, 0, ml, ml, ff, wc, N)

def helicity_amps_deltaC7(q2, deltaC7_dict, par, B, V, lep):
    r"""A function returning a contribution to the helicity amplitudes in
    $B\to V\ell^+\ell^-$ coming from an effective helicity-dependent shift of
    the Wilson coefficient $C_7(\mu_b)$. This can be used to parametrize
    residual uncertainties due to subleading non-factorizable hadronic effects.

    The input dictionary `deltaC7_dict` should be of the form
    { ('0','V'): deltaC7_0, ('pl','V'): deltaC7_pl, ('mi','V'): deltaC7_mi }
    """
    ha = {}
    for amp in [('0','V'), ('pl','V'), ('mi','V')]:
        ha[amp] = _helicity_amps_deltaC(q2, deltaC7_dict[amp], '7', par, B, V, lep)[amp]
    return ha

def helicity_amps_deltaC9(q2, deltaC9_dict, par, B, V, lep):
    r"""A function returning a contribution to the helicity amplitudes in
    $B\to V\ell^+\ell^-$ coming from an effective helicity-dependent shift of
    the Wilson coefficient $C_7(\mu_b)$. This can be used to parametrize
    residual uncertainties due to subleading non-factorizable hadronic effects.

    The input dictionary `deltaC9_dict` should be of the form
    { ('0','V'): deltaC9_0, ('pl','V'): deltaC9_pl, ('mi','V'): deltaC9_mi }
    """
    ha = {}
    for amp in [('0','V'), ('pl','V'), ('mi','V')]:
        ha[amp] = _helicity_amps_deltaC(q2, deltaC9_dict[amp], 'v', par, B, V, lep)[amp]
    return ha

# One possibility is to parametrize the effective shift in C7 or C9 as a simple
# polynomial in q2.

def helicity_amps_deltaC7_polynomial(q2, par, B, V, lep):
    deltaC7_0   =( par[B+'->'+V+' deltaC7 a_0 Re']  + par[B+'->'+V+' deltaC7 b_0 Re'] *q2
             +1j*( par[B+'->'+V+' deltaC7 a_0 Im']  + par[B+'->'+V+' deltaC7 b_0 Im'] *q2 ))
    deltaC7_pl  =( par[B+'->'+V+' deltaC7 a_+ Re']  + par[B+'->'+V+' deltaC7 b_+ Re'] *q2
             +1j*( par[B+'->'+V+' deltaC7 a_+ Im']  + par[B+'->'+V+' deltaC7 b_+ Im'] *q2 ))
    deltaC7_mi  =( par[B+'->'+V+' deltaC7 a_- Re']  + par[B+'->'+V+' deltaC7 b_- Re'] *q2
             +1j*( par[B+'->'+V+' deltaC7 a_- Im']  + par[B+'->'+V+' deltaC7 b_- Im'] *q2 ))
    deltaC7_dict = { ('0','V'): deltaC7_0, ('pl','V'): deltaC7_pl, ('mi','V'): deltaC7_mi }
    return helicity_amps_deltaC7(q2, deltaC7_dict, par, B, V, lep)

# note that, when parametrizing the correction as a shift to C9 rather than C7,
# the contribution to the transverse (+ and -) amplitudes has to start with
# 1/q2, otherwise one effectively sets corrections to B->Vgamma to zero.
def helicity_amps_deltaC9_polynomial(q2, par, B, V, lep):
    deltaC9_0   =( par[B+'->'+V+' deltaC9 a_0 Re']  + par[B+'->'+V+' deltaC9 b_0 Re'] *q2
             +1j*( par[B+'->'+V+' deltaC9 a_0 Im']  + par[B+'->'+V+' deltaC9 b_0 Im'] *q2 ))
    deltaC9_pl  =( par[B+'->'+V+' deltaC9 a_+ Re']/q2  + par[B+'->'+V+' deltaC9 b_+ Re']
             +1j*( par[B+'->'+V+' deltaC9 a_+ Im']/q2  + par[B+'->'+V+' deltaC9 b_+ Im'] ))
    deltaC9_mi  =( par[B+'->'+V+' deltaC9 a_- Re']/q2  + par[B+'->'+V+' deltaC9 b_- Re']
             +1j*( par[B+'->'+V+' deltaC9 a_- Im']/q2  + par[B+'->'+V+' deltaC9 b_- Im'] ))
    deltaC9_dict = { ('0','V'): deltaC9_0, ('pl','V'): deltaC9_pl, ('mi','V'): deltaC9_mi }
    return helicity_amps_deltaC9(q2, deltaC9_dict, par, B, V, lep)

# a constant shift, e.g. for high q^2
def helicity_amps_deltaC9_constant(q2, par, B, V, lep):
    deltaC9_0   = par[B+'->'+V+' deltaC9 c_0 Re'] + 1j*par[B+'->'+V+' deltaC9 c_0 Im']
    deltaC9_pl   = par[B+'->'+V+' deltaC9 c_pl Re'] + 1j*par[B+'->'+V+' deltaC9 c_pl Im']
    deltaC9_mi   = par[B+'->'+V+' deltaC9 c_mi Re'] + 1j*par[B+'->'+V+' deltaC9 c_mi Im']
    deltaC9_dict = { ('0','V'): deltaC9_0, ('pl','V'): deltaC9_pl, ('mi','V'): deltaC9_mi }
    return helicity_amps_deltaC9(q2, deltaC9_dict, par, B, V, lep)


# Functions returning functions needed for Implementation
def fct_deltaC7_polynomial(B, V, lep):
    def fct(wc_obj, par_dict, q2, cp_conjugate):
        par = par_dict.copy()
        if cp_conjugate:
            par = conjugate_par(par)
        return helicity_amps_deltaC7_polynomial(q2, par, B, V, lep)
    return fct

def fct_deltaC9_polynomial(B, V, lep):
    def fct(wc_obj, par_dict, q2, cp_conjugate):
        par = par_dict.copy()
        if cp_conjugate:
            par = conjugate_par(par)
        return helicity_amps_deltaC9_polynomial(q2, par_dict, B, V, lep)
    return fct

def fct_deltaC9_constant(B, V, lep):
    def fct(wc_obj, par_dict, q2, cp_conjugate):
        par = par_dict.copy()
        if cp_conjugate:
            par = conjugate_par(par)
        return helicity_amps_deltaC9_constant(q2, par_dict, B, V, lep)
    return fct

# AuxiliaryQuantity & Implementatation: subleading effects at LOW q^2

for had in [('B0','K*0'), ('B+','K*+'), ('Bs','phi'), ]:
    for l in ['e', 'mu', ]:
        process = had[0] + '->' + had[1] + l+l # e.g. B0->K*0mumu
        quantity = process + ' subleading effects at low q2'
        a = AuxiliaryQuantity(name=quantity, arguments=['q2', 'cp_conjugate'])
        a.description = ('Contribution to ' + process + ' helicity amplitudes from'
                        ' subleading hadronic effects (i.e. all effects not included'
                        r'elsewhere) at $q^2$ below the charmonium resonances')

        # Implementation: C7-polynomial
        iname = process + ' deltaC7 polynomial'
        i = Implementation(name=iname, quantity=quantity,
                       function=fct_deltaC7_polynomial(B=had[0], V=had[1], lep=l))
        i.set_description(r"Effective shift in the Wilson coefficient $C_7(\mu_b)$"
                          r" as a first-order polynomial in $q^2$.")

        # Implementation: C9-polynomial
        iname = process + ' deltaC9 polynomial'
        i = Implementation(name=iname, quantity=quantity,
                       function=fct_deltaC9_polynomial(B=had[0], V=had[1], lep=l))
        i.set_description(r"Effective shift in the Wilson coefficient $C_9(\mu_b)$"
                          r" as a first-order polynomial in $q^2$.")


# AuxiliaryQuantity & Implementatation: subleading effects at HIGH q^2

for had in [('B0','K*0'), ('B+','K*+'), ('Bs','phi'), ]:
    for l in ['e', 'mu', ]:
        process = had[0] + '->' + had[1] + l+l # e.g. B0->K*0mumu
        quantity = process + ' subleading effects at high q2'
        a = AuxiliaryQuantity(name=quantity, arguments=['q2', 'cp_conjugate'])
        a.description = ('Contribution to ' + process + ' helicity amplitudes from'
                        ' subleading hadronic effects (i.e. all effects not included'
                        r'elsewhere) at $q^2$ above the charmonium resonances')

        # Implementation: C9 constant shift
        iname = process + ' deltaC9 shift'
        i = Implementation(name=iname, quantity=quantity,
                       function=fct_deltaC9_constant(B=had[0], V=had[1], lep=l))
        i.set_description(r"Effective constant shift in the Wilson coefficient $C_9(\mu_b)$.")