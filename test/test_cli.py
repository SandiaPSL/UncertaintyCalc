''' Test command-line interface '''

import os
import subprocess
import numpy as np
from scipy import stats

import psluncert as uc
from psluncert import project
from psluncert import reverse
from psluncert import risk
from psluncert import curvefit
from psluncert import output
from psluncert import customdists


def test_file():
    ''' Test running a yaml file '''
    fname = 'test/ex_expansion.yaml'
    u = project.Project.from_configfile(fname)
    u.calculate()
    with output.report_format('text', 'text'):
        report = str(u.report_short())
    s = subprocess.run(['psluncertf', fname], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report2 = s.stdout.decode('utf-8').replace('\r', '')   # Windows adds \r to every \n, whether there's already an \r or not...?
    assert report == report2


def test_uc():
    ''' Test uncertainty calc '''
    u = uc.UncertCalc('f = a * b + c', seed=4848484)
    u.set_input('a', nom=10, std=1)
    u.set_input('b', nom=5, dist='uniform', a=.5)
    u.set_input('c', nom=3, unc=3, k=2)
    u.correlate_vars('a', 'b', .6)
    u.correlate_vars('c', 'b', -.3)
    out = u.calculate()
    with output.report_format('text', 'text'):
        report = str(out.report())

    s = subprocess.run(['psluncert', 'f=a*b+c', '--variables', 'a=10', 'b=5', 'c=3', '--uncerts', 'a; std=1', 'b; dist=uniform; a=.5', 'c; unc=3; k=2', '--correlate', 'a; b; .6', 'c; b; -.3'],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report2 = s.stdout.decode('utf-8').replace('\r', '')
    assert report == report2

    # HTML format
    with output.report_format('mpl', 'svg'):
        reporthtml = out.report().get_html()
    s = subprocess.run(['psluncert', 'f=a*b+c', '--variables', 'a=10', 'b=5', 'c=3', '--uncerts', 'a; std=1', 'b; dist=uniform; a=.5', 'c; unc=3; k=2', '--correlate', 'a; b; .6', 'c; b; -.3', '-f', 'html'],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report2html = s.stdout.decode('utf-8').replace('\r', '')
    assert reporthtml == report2html

    # MD format
    with output.report_format('mpl', 'svg'):
        reportmd = out.report().get_md()
    s = subprocess.run(['psluncert', 'f=a*b+c', '--variables', 'a=10', 'b=5', 'c=3', '--uncerts', 'a; std=1', 'b; dist=uniform; a=.5', 'c; unc=3; k=2', '--correlate', 'a; b; .6', 'c; b; -.3', '-f', 'md'],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report2md = s.stdout.decode('utf-8').replace('\r', '')
    assert reportmd == report2md


def test_rev():
    ''' Test reverse calc '''
    expr = 'rho = w / (k*d**2*h)'
    k = 12.870369  # pi/4*2.54**3, no uncertainty
    h = .5  # inch
    d = .25 # inch
    ud = .001/2
    uh = .001/2

    # Required values for rho
    rho = 2.0  # g/cm3
    urho = .06/2

    np.random.seed(234283742)
    u = reverse.UncertReverse(expr, solvefor='w', targetnom=rho, targetunc=urho)
    u.set_input('h', nom=h, std=uh)
    u.set_input('d', nom=d, std=ud)
    u.set_input('k', nom=k)
    u.add_required_inputs()
    out = u.calculate()
    with output.report_format('text', 'text'):
        report = str(out.report())

    s = subprocess.run(['psluncertrev', 'rho=w/(k*d**2*h)', '--target={}'.format(rho), '--targetunc={}'.format(urho), '--solvefor=w', '--variables', 'h=.5', 'd=.25', 'k=12.870369',
                        '--uncerts', 'h; std=.0005', 'd; std=.0005'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report2 = s.stdout.decode('utf-8').replace('\r', '')
    assert report == report2

    # HTML format
    with output.report_format('mpl', 'svg'):
        reporthtml = out.report().get_html()
    s = subprocess.run(['psluncertrev', 'rho=w/(k*d**2*h)', '--target={}'.format(rho), '--targetunc={}'.format(urho), '--solvefor=w', '--variables', 'h=.5', 'd=.25', 'k=12.870369',
                        '--uncerts', 'h; std=.0005', 'd; std=.0005', '-f', 'html'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report2html = s.stdout.decode('utf-8').replace('\r', '')
    assert reporthtml == report2html


def test_risk():
    ''' Test risk analysis command line '''
    # Normal risk report with test distribution and guardband
    u = risk.UncertRisk(dproc=stats.norm(loc=0, scale=4), dtest=stats.norm(loc=0, scale=1))
    u.set_guardband(.2, .2)
    u.calculate()
    with output.report_format('text', 'text'):
        report = str(u.out.report())
    s = subprocess.run(['psluncertrisk', '--procdist', 'loc=0; scale=4', '--testdist', 'loc=0; scale=1', '-LL', '-2', '-UL', '2', '-GBL', '.2', '-GBU', '.2'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report2 = s.stdout.decode('utf-8').replace('\r', '')
    assert report == report2

    # Without test distribution
    u = risk.UncertRisk(dproc=stats.norm(loc=0, scale=4), dtest=None)
    u.calculate()
    with output.report_format('text', 'text'):
        report = str(u.out.report())
    s = subprocess.run(['psluncertrisk', '--procdist', 'loc=0; scale=4', '-LL', '-2', '-UL', '2'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report2 = s.stdout.decode('utf-8').replace('\r', '')
    assert report == report2

    # With non-normal distribution
    u = risk.UncertRisk(dproc=customdists.uniform(a=2), dtest=stats.norm(loc=0, scale=.5))
    u.calculate()
    with output.report_format('text', 'text'):
        report = str(u.out.report())
    s = subprocess.run(['psluncertrisk', '--procdist', 'dist=uniform; a=2; median=0', '--testdist', 'loc=0; scale=.5', '-LL', '-2', '-UL', '2'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report2 = s.stdout.decode('utf-8').replace('\r', '')
    assert report == report2

    # With plots/verbose
    u = risk.UncertRisk(dproc=stats.norm(loc=0, scale=4), dtest=stats.norm(loc=0, scale=1))
    u.calculate()
    with output.report_format('text', 'text'):
        report = str(u.out.report_all())
    s = subprocess.run(['psluncertrisk', '--procdist', 'loc=0; scale=4', '--testdist', 'loc=0; scale=1', '-LL', '-2', '-UL', '2', '-v'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report2 = s.stdout.decode('utf-8').replace('\r', '')
    assert report == report2


def test_curve():
    ''' Test Curve fit command line '''
    x = np.array([30,100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500])
    y = np.array([4642,4612,4565,4513,4476,4433,4389,4347,4303,4251,4201,4140,4100,4073,4024,3999])
    arr = curvefit.Array(x, y)
    fit = curvefit.CurveFit(arr)
    fit.calculate(gum=True, lsq=True)
    with output.report_format('text', 'text'):
        report = str(fit.out.report())

    x = ['{}'.format(k) for k in x]
    y = ['{}'.format(k) for k in y]
    s = subprocess.run(['psluncertfit', '-x', *x, '-y', *y, '--methods', 'lsq', 'gum'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report2 = s.stdout.decode('utf-8').replace('\r', '')
    assert report == report2
