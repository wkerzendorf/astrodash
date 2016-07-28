from create_arrays import *
import pickle

class CreateTrainingSet(object):

    def __init__(self, snidTemplateLocation, snidtempfilelist, sfTemplateLocation, sftempfilelist, w0, w1, nw, nTypes, minAge, maxAge, ageBinSize):
        self.snidTemplateLocation = snidTemplateLocation
        self.snidtempfilelist = snidtempfilelist
        self.sfTemplateLocation = sfTemplateLocation
        self.sftempfilelist = sftempfilelist
        self.w0 = w0
        self.w1 = w1
        self.nw = nw
        self.nTypes = nTypes
        self.minAge = minAge
        self.maxAge = maxAge
        self.ageBinSize = ageBinSize
        self.ageBinning = AgeBinning(self.minAge, self.maxAge, self.ageBinSize)
        self.numOfAgeBins = self.ageBinning.age_bin(self.maxAge) + 1
        self.nLabels = self.nTypes * self.numOfAgeBins
        self.z = 0
        self.createArrays = CreateArrays(self.w0, self.w1, self.nw, self.nTypes, self.minAge, self.maxAge, self.ageBinSize, self.z)
        self.arrayTools = ArrayTools(self.nLabels)
        
    def type_amounts(self, labels):
        counts = self.arrayTools.count_labels(labels)

        return counts


    def all_templates_to_arrays(self):
        images = np.empty((0, int(self.nw)), np.float32)  # Number of pixels
        labels = np.empty((0, self.nTypes), float)  # Number of labels (SN types)
        typeList = []

        typelistSnid, imagesSnid, labelsSnid, filenamesSnid, typeNamesSnid = self.createArrays.snid_templates_to_arrays(self.snidTemplateLocation, self.snidtempfilelist)
        # imagesSuperfit, labelsSuperfit, filenamesSuperfit, typeNamesSuperfit = superfit_templates_to_arrays(self.sfTemplateLocation, sftempfilelist)

        images = np.vstack((imagesSnid))  # , imagesSuperfit)) #Add in other templates from superfit etc.
        labels = np.vstack((labelsSnid))  # , labelsSuperfit))
        filenames = np.hstack((filenamesSnid))  # , filenamesSuperfit))
        typeNames = np.hstack((typeNamesSnid))

        typeList = typelistSnid

        imagesShuf, labelsShuf, filenamesShuf, typeNamesShuf = self.arrayTools.shuffle_arrays(images, labels, filenames, typeNames)  # imagesShortlist, labelsShortlist = shortlist_arrays(images, labels)

        typeAmounts = self.type_amounts(labels)
        
        return typeList, imagesShuf, labelsShuf, filenamesShuf, typeNamesShuf, typeAmounts  # imagesShortlist, labelsShortlist


    def sort_data(self):
        trainPercentage = 0.8
        testPercentage = 0.2
        validatePercentage = 0.

        typeList, images, labels, filenames, typeNames, typeAmounts = self.all_templates_to_arrays()
        # imagesSuperfit, labelsSuperfit, filenamesSuperfit = superfit_templates_to_arrays(sftempfilelist)
        # imagesSuperfit, labelsSuperfit, filenamesSuperfit = shuffle_arrays(imagesSuperfit, labelsSuperfit, filenamesSuperfit)


        trainSize = int(trainPercentage * len(images))
        testSize = int(testPercentage * len(images))

        trainImages = images[:trainSize]
        testImages = images[trainSize: trainSize + testSize]
        validateImages = images[trainSize + testSize:]
        trainLabels = labels[:trainSize]
        testLabels = labels[trainSize: trainSize + testSize]
        validateLabels = labels[trainSize + testSize:]
        trainFilenames = filenames[:trainSize]
        testFilenames = filenames[trainSize: trainSize + testSize]
        validateFilenames = filenames[trainSize + testSize:]
        trainTypeNames = typeNames[:trainSize]
        testTypeNames = typeNames[trainSize: trainSize + testSize]
        validateTypeNames = typeNames[trainSize + testSize:]

        trainImagesOverSample, trainLabelsOverSample, trainFilenamesOverSample, trainTypeNamesOverSample = self.arrayTools.over_sample_arrays(trainImages, trainLabels, trainFilenames, trainTypeNames)
        testImagesShortlist, testLabelsShortlist, testFilenamesShortlist, testTypeNamesShortlist = testImages, testLabels, testFilenames, testTypeNames  # (testImages, testLabels, testFilenames)

        return ((trainImagesOverSample, trainLabelsOverSample, trainFilenamesOverSample, trainTypeNamesOverSample),
                (testImagesShortlist, testLabelsShortlist, testFilenamesShortlist, testTypeNamesShortlist),
                (validateImages, validateLabels, validateFilenames, validateTypeNames),
                typeAmounts)


class SaveTrainingSet(object):
    def __init__(self, snidTemplateLocation, snidtempfilelist, sfTemplateLocation, sftempfilelist, w0, w1, nw, nTypes, minAge, maxAge, ageBinSize):
        self.snidTemplateLocation = snidTemplateLocation
        self.snidtempfilelist = snidtempfilelist
        self.sfTemplateLocation = sfTemplateLocation
        self.sftempfilelist = sftempfilelist
        self.w0 = w0
        self.w1 = w1
        self.nw = nw
        self.nTypes = nTypes
        self.minAge = minAge
        self.maxAge = maxAge
        self.ageBinSize = ageBinSize
        self.createLabels = CreateLabels(self.nTypes, self.minAge, self.maxAge, self.ageBinSize)
        
        self.createTrainingSet = CreateTrainingSet(self.snidTemplateLocation, self.snidtempfilelist, self.sfTemplateLocation, self.sftempfilelist, self.w0, self.w1, self.nw, self.nTypes, self.minAge, self.maxAge, self.ageBinSize)
        self.sortData = self.createTrainingSet.sort_data()
        self.trainImages = self.sortData[0][0]
        self.trainLabels = self.sortData[0][1]
        self.trainFilenames = self.sortData[0][2]
        self.trainTypeNames = self.sortData[0][3]
        self.testImages = self.sortData[1][0]
        self.testLabels = self.sortData[1][1]
        self.testFilenames = self.sortData[1][2]
        self.testTypeNames = self.sortData[1][3]
        self.validateImages = self.sortData[2][0]
        self.validateLabels = self.sortData[2][1]
        self.validateFilenames = self.sortData[2][2]
        self.validateTypeNames = self.sortData[2][3]
        self.typeAmounts = self.sortData[3]

        self.typeNamesList = self.createLabels.type_names_list()


    def type_amounts(self):
        for i in range(len(self.typeNamesList)):
            print(str(self.typeAmounts[i]) + ": " + str(self.typeNamesList[i]))
        return self.typeNamesList, self.typeAmounts

    def save_arrays(self):
        np.savez_compressed('file_w_ages2.npz', trainImages=self.trainImages, trainLabels=self.trainLabels,
                        trainFilenames=self.trainFilenames, trainTypeNames=self.trainTypeNames,
                        testImages=self.testImages, testLabels=self.testLabels,
                        testFilenames=self.testFilenames, testTypeNames=self.testTypeNames,
                        typeNamesList = self.typeNamesList)
        


with open('training_params.pickle') as f:
    nTypes, w0, w1, nw, minAge, maxAge, ageBinSize = pickle.load(f)
    
snidTemplateLocation = '/home/dan/Desktop/SNClassifying_Pre-alpha/templates/'
sfTemplateLocation = '/home/dan/Desktop/SNClassifying_Pre-alpha/templates/superfit_templates/sne/'
snidtempfilelist1 = snidTemplateLocation + 'templist'
sftempfilelist1 = sfTemplateLocation + 'templist.txt'

saveTrainingSet = SaveTrainingSet(snidTemplateLocation, snidtempfilelist1, sfTemplateLocation, sftempfilelist1, w0, w1, nw, nTypes, minAge, maxAge, ageBinSize)
typeNamesList, typeAmounts = saveTrainingSet.type_amounts()

saveTrainingSet.save_arrays()