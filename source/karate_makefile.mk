######################### DEFINITIONS ############################

# Define the commandline invocation of Maven if necessary:
ifeq ($(MVN),)
    MVN  := mvn
endif

######################## BUILD TARGETS ###########################

.PHONY: archtype

archetype:
	@ mvn archetype:generate -DarchetypeGroupId=com.intuit.karate -DarchetypeArtifactId=karate-archetype -DarchetypeVersion=1.2.0 -DgroupId=com.ordillanLabs -DartifactId=KarateOperationsAutomation -Dversion=0.1-SNAPSHOT

help:
	@ echo "Usage   :  make <target>"
	@ echo "Targets :"
	@ echo "   archetype ........... Generates the project archetype"
