import numpy as np 
import pandas
import scipy.special as spec
from scipy import integrate
import warnings


def supression(lambda_N=100, theta=0,E_mu=20,gamma=1.7,X_0=37, alphax0 = 2):
	"""
	Returns supression factor for theoretical formula, all defualt constants are taken from ref. [5] in project
	"""
	p_1 = 1/(E_mu*np.cos(theta) + alphax0)
	warnings.filterwarnings('ignore')
	return ((lambda_N*np.cos(theta))/X_0)**p_1 * ((E_mu)/(E_mu + alphax0/np.cos(theta)))**(p_1 + gamma + 1) * spec.gamma(p_1 + 1)

def theory(E_mu=1,theta=0):
	"""
	An extrapolation formula valid for neglidgible Muon decay for a given energy of Muon E-mu and Zenith angle theta.
	i.e. E_mu > 100/cos(theta) Gev and Earth curvature neglected
	i.e. theta > 70 degrees

	E_mu in Gev; theta in radians

	Defaults are E_mu=1 GeV and theta=0
	"""
	return 1400*E_mu**(-2.7) * ((1 + 1.1*E_mu*np.cos(theta)/115)**(-1) + 0.054*(1 + 1.11*E_mu*np.cos(theta)/850)**(-1) )

def theory_supressed(lambda_N=100, theta=0,E_mu=20,gamma=1.7,X_0=37, alphax0 = 2):
	"""
	Gives supressed theory, i.e. supression()*theory()
	"""
	return supression(lambda_N=lambda_N, theta=theta,E_mu=E_mu,gamma=gamma,X_0=X_0, alphax0 = alphax0)*theory(E_mu=E_mu,theta=theta)

def best_fit(E_mu=20):
	"""
	This function gives the result of the best fit order-3 polynomial calculated for a large composite dataset of sea-level cosmic ray measurments:

	f(x) = 0.0802084387362498x^3 − 0.865540849689325x^2 − 0.529814522816601x + 1.30273127415449

	where f(x) = log10(Flux) and x = log10(E_mu)
	"""
	log10 = np.log10(E_mu)
	return np.power(10, (0.0802084387362498*log10**3 - 0.865540849689325*log10**2 - 0.529814522816601*log10 + 1.30273127415449))


def element_resolve(particle):
	"""
	Takes element name, symbol or atomic number (Z) and returns mass number (A)
	"""
	try:
		element_file = pandas.read_csv("elements.csv",header=0,delimiter='\t')
	except:
		raise Exception("ensure elements.csv is present and available to your shell/this python script")
	
	if isinstance(particle,int):
		try:
			return float(element_file.loc[element_file["AtomicNumber"]==particle].MassNumber)
		except:
			raise Exception("Error: atomic number not valid (must be int <=82")
	
	elif isinstance(particle,str) and len(particle)<=2:
		try:
			return float(element_file.loc[element_file["Symbol"]==particle].MassNumber)
		except:
			raise Exception("Error: particle symbol is not valid in the dictionary")
	elif isinstance(particle,str):
		try:
			return float(element_file.loc[element_file["Name"]==particle].MassNumber)
		except:
			raise Exception("Error: particle name is not valid in the dictionary")
	else:
		raise Exception("particle input invalid type")




def composite(E_mu=0, cutoff=18857, truncate=0.1,theta=0):
	"""
	Evaluates either theory_supressed() (with theta=0) or best_fit() depending on range,
	the default lower cutoff being their coincidence at 18857 GeV. Input values below truncate 
	(default= 0.1 GeV) will return zero.
	"""
	if (theta != 0):
		raise Exception("Composite_function cannnot take non-zero Zenith angles") 
	#return np.where(E_mu<cutoff,np.where(E_mu < truncate, 0, best_fit(E_mu=E_mu)),theory_supressed(E_mu=E_mu))
	if E_mu<=cutoff:
		return best_fit(E_mu=E_mu)
	return theory_supressed(E_mu=E_mu)

def scaledTheory(theta,E_mu):
    scale=composite(E_mu=E_mu)/theory_supressed(E_mu=E_mu,theta=0)
    return scale*theory_supressed(theta=theta,E_mu=E_mu)

def integrated_theory(E_mu):
    return np.float64(integrate.quad(scaledTheory, a=0, b=np.pi/2,args=(E_mu,))[0])

def integrated_fast(E_mu):
	coeffs=np.array([ 3.88611063e-04, -6.90846085e-03,  3.67707268e-02,  1.93046252e-02,\
        -8.82281166e-01,  2.72979821e+00,  1.17488991e+00])
	g=np.poly1d(coeffs)
	return (10**g(np.log10(E_mu)))/E_mu**3

# def integrated_fast(E_mu):
# 	coeffs=np.array(([ 4.05232241e-04, -7.30338740e-03,  4.05996475e-02,  1.06852527e-03,
#         -8.53022670e-01,  2.82746788e+00,  7.69578851e-01]))
# 	g=np.poly1d(coeffs)
# 	return (10**g(np.log10(E_mu)))/E_mu**3