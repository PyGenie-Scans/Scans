import genie_python.genie as gen
import LSS.SANSroutines as lm

def echoscan_axis(scan, frms, rtitle, save=False):
    gen.abort()
    lm.setuplarmor_echoscan()

    gen.change(title=rtitle)
    gen.change(nperiods=npoints*2)

    gen.begin(paused=1)
    # setup the scan arrays and figure
    xval=[0]*npoints
    yval=[0]*npoints
    eval=[0]*npoints

    stepsize=(endval-startval)/float(npoints-1)
    for i in range(npoints):
        xval[i]=(startval+i*stepsize)

    mpl.ion()
    fig1=mpl.figure(1)
    mpl.clf()
    ax = mpl.subplot(111)
    #ax.set_xlim((0,4))
    ax.set_xlabel(axis)
    ax.set_ylabel('Neutorn Polarisation')
    # reasonable x-Axis, necessary to get the full window from the first datapoint
    scanrange = np.absolute(endval - startval)
    mpl.xlim((startval-scanrange*0.05, endval+scanrange*0.05))
    mpl.draw()
    mpl.pause(0.001)
    flipper1(1)

    colors = ['ko', "r^", "gd", "bs"]

    for i in range(npoints):
        gen.change(period=(i*2)+1)
        cset_str(axis,xval[i])
        flipper1(1)
        gen.waitfor_move()
        gfrm=gen.get_frames()
        resume()
        gen.waitfor(frames=gfrm+frms)
        pause()
        flipper1(0)
        gen.change(period=(i*2)+2)
        gfrm=gen.get_frames()
        resume()
        gen.waitfor(frames=gfrm+frms)
        pause()

        # wavelength range 1 3-5Ang
        a1=gen.get_spectrum(1,(i*2)+1)
        msigup=sum(a1['signal'])*100.0
        mesigup=(np.sqrt(msigup))

        a1=gen.get_spectrum(1,(i*2)+2)
        msigdo=sum(a1['signal'])*100.0
        mesigdo=(np.sqrt(msigdo))

        sigup = []
        sigdo = []
        for slc in [slice(222,666), slice(222, 370), slice(370, 518), slice(518, 666)]:
            a1=gen.get_spectrum(11,(i*2)+1)
            sigup.append(sum(a1['signal'][slc])*100.0)
            a1=gen.get_spectrum(12,(i*2)+1)
            sigup[-1] += sum(a1['signal'][slc])*100.0

            a1=gen.get_spectrum(11,(i*2)+2)
            sigdo.append(sum(a1['signal'][slc])*100.0)
            a1=gen.get_spectrum(12,(i*2)+2)
            sigdo[-1] += sum(a1['signal'][slc])*100.0
        sigup = np.array(sigup, dtype=np.float64)
        sigdo = np.array(sigdo, dtype=np.float64)
        esigdo = np.sqrt(sigdo)
        esigup = np.sqrt(sigup)
        print("--------")
        print(xval[i])
        print(sigup)
        print(sigdo)

        yval[i]=(sigup-sigdo)/(sigup+sigdo)
        eval[i]=yval[i]*np.sqrt(esigdo**2+esigup**2)*np.sqrt((sigup-sigdo)**-2+(sigup+sigdo)**-2)
        #eval[i]=yval[i]*np.sqrt(esido**2+esidup**2)*np.sqrt((sigup-sigdn)**-2+(sigup+sigdn)**-2)
        #eval[i]=yval[i]*1e-3
        #eval[i]=(sqrt((sig/(msig*msig))+(sig*sig/(msig*msig*msig))))
        for idx, clr in enumerate(colors):
            ax.errorbar(xval[i], yval[i][idx], eval[i][idx], fmt = clr)
            if i > 0:
                ax.plot([xval[i-1], xval[i]], [yval[i-1][idx], yval[i][idx]], clr[0])
        fig1.canvas.draw()
        mpl.pause(0.001)
    if save:
        end()
    else:
        abort()

    xval = np.array(xval)
    yval = np.array(yval)
    eval = np.array(eval)

    print(xval.shape)
    print(yval.shape)
    print(eval.shape)

    def model(x, center, amp, freq, width):
        return amp * np.cos((x-center)*freq)*np.exp(-((x-center)/width)**2)

    # popt, _ = curve_fit(model, xval, yval[:, 0], [6.5, 1, 1, 10], sigma=eval[:, 0])
    # ax.plot(xval, model(xval, *popt), "-")
    # fig1.canvas.draw()
    # print("The center is {}".format(popt[0]))

    centers = []
    xplot = np.linspace(np.min(xval), np.max(xval), 1001)
    guess = xval[np.argmax(yval[:, 0])]
    popt = [guess, 1, 2*np.pi/(750.0), endval-startval]
    mpl.clf()
    ax = mpl.subplot(111)
    #ax.set_xlim((0,4))
    ax.set_xlabel(axis)
    ax.set_ylabel('Neutron Polarisation')
    for i in range(yval.shape[1]):
        popt, _ = curve_fit(model, xval, yval[:, i], popt, sigma=eval[:, 0])
        ax.errorbar(xval, yval[:, i], yerr=eval[:, i], fmt=colors[i])
        ax.plot(xplot, model(xplot, *popt), colors[i][:-1]+"-")
        centers.append(popt[0])
    fig1.canvas.draw()
    mpl.pause(0.001)

    value = np.mean(centers)
    error = np.std(centers)
    digits = -1*int(np.floor(np.log(error)/np.log(10)))
    value = np.around(value, digits)
    error = np.around(error, digits)
    print("The center is {} +- {}".format(value, error))
    mpl.ioff()
    return (value, error)
