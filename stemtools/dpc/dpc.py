from scipy import ndimage as scnd
from scipy import optimize as sio
import numpy as np
import numba

@numba.jit(cache=True)
def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

@numba.jit(cache=True)
def pol2cart(rho, phi):
    x = np.multiply(rho,np.cos(phi))
    y = np.multiply(rho,np.sin(phi))
    return(x, y)

@numba.jit(cache=True)
def angle_fun(angle,rho_dpc,phi_dpc):
    angle = angle*((np.pi)/180)
    new_phi = phi_dpc + angle
    x_dpc,y_dpc = pol2cart(rho_dpc,new_phi)
    charge = np.gradient(x_dpc)[1] + np.gradient(y_dpc)[0]
    angle_sum = np.sum(np.abs(charge))
    return angle_sum

@numba.jit(cache=True)
def optimize_angle(rho_dpc,phi_dpc):
    x0 = 90
    x = sio.minimize(angle_fun,x0,args=(rho_dpc,phi_dpc))
    min_x = x.x
    sol1 = min_x - 90
    sol2 = min_x + 90
    return sol1,sol2

@numba.jit(parallel=True)
def calculate_dpc(data4D):
    data_size = (np.asarray(data4D.shape)).astype(int)
    rho_shift = (np.zeros((data_size[2],data_size[3])))
    phi_shift = (np.zeros((data_size[2],data_size[3])))
    Mean_r = np.mean(np.mean(data4D,axis=3),axis=2)
    center_x,center_y,data_radius = circle_fit(canny_edge(scnd.median_filter(Mean_r,2),0.2,0.8))
    for jj in numba.prange(data_size[3]):
        for ii in range(data_size[2]):
            ronchigram = scnd.median_filter(data4D[:,:,ii,jj],2)
            com_x,com_y = scnd.measurements.center_of_mass(ronchigram)
            shift_x = com_x - center_x
            shift_y = com_y - center_y
            rho,phi = cart2pol(shift_x,shift_y)
            rho_shift[ii,jj] = rho
            phi_shift[ii,jj] = phi
    return(rho_shift, phi_shift)