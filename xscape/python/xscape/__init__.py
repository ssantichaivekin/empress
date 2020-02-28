#
# Python module for xscape library
#

# add pre-bundled dependencies to the python path,
# if they are not available already

#=============================================================================
# constants

PROGRAM_NAME = u"xscape"
PROGRAM_VERSION_MAJOR = 0
PROGRAM_VERSION_MINOR = 0
PROGRAM_VERSION_RELEASE = 5
PROGRAM_VERSION = (PROGRAM_VERSION_MAJOR,
                   PROGRAM_VERSION_MINOR,
                   PROGRAM_VERSION_RELEASE)

if PROGRAM_VERSION_RELEASE != 0:
    PROGRAM_VERSION_TEXT = "%d.%d.%d" % (PROGRAM_VERSION_MAJOR,
                                         PROGRAM_VERSION_MINOR,
                                         PROGRAM_VERSION_RELEASE)
else:
    PROGRAM_VERSION_TEXT = "%d.%d" % (PROGRAM_VERSION_MAJOR,
                                      PROGRAM_VERSION_MINOR)
