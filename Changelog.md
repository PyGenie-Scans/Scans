v0.3
----

- Detectors
  - time estimation is now universal and doesn't need to be
	reimplemented for each beamline.
  - The `measure` function of the detector class has been removed,
	as it was both unused and superceded by the generic detector facility.
- Documentation
  - Updated Guide for Instrument Scientists.
- Interface
  - Added SPEC compatability layer with functions ascan and dscan.

v0.2
----

- Fitting
  - Added PeakFit class for trivial peak finding among fitters
  - Removed warnings filter on CurveFit.  Adding the filter required
	importing scipy, which is still giving us trouble.  Since the
	CurveFit instances are already triggering the Ctrl-C bug and we're
	trying to avoid them, having an extra ugly warning message is not
	worth fighting.
  - Added TrapezoidFit for fitting trapezoidal curves
  - Added ErrorFit for finding edges
- Mock instrument
  - Changed the simulated detector's output to now include a peak.
	This makes many fitting options much easier to test.
  - Adds Mocks module for having a shared mock instrument across
	multiple modules.
- Larmor
  - Added support for Mocking when not on the actual larmor beamline
  - Return a proper Monoid (Average) from the default detector
  - Normalise the default detector against the upstream monitor
  - Change pol_measure to run in a single DAE measurement
- Monoid
  - Handled more zero cases
  - Fixed several missing return statements
  - Fix polarisation bug
- Motion
  - Add support for limits on motors
- Scans
  - When fitting on a detector that returns multiple values, return
	the median value, instead of the mean.  The median is less
	sensitive to outliers.
  - Remove return_values and return_figure from fitting plot
- Zoom
  - Create detectors for monitors 1-4
  - Return proper monoid (Sum) from monitor
- Plotting
  - Support multiplotting when in the IBEX console
- Misc
  - Simplifying importing down to `from Scans import *`
