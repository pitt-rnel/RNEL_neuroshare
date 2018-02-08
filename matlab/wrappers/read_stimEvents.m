function [stimData] = read_stimEvents(dataPath, NEVfilenum, varargin)
    
    %   DESCRIPTION
    %   ===================================================================
    %   Reads continuous data for input channels from specified NS5/NF3 file 
    %
    %   INPUTS
    %   ===================================================================
    %   dataPath        : (char) path to data file
    %   dataStream      : (char) 'hi-res'/'raw'/'analog'
    %   channels        : (int) 1xn vector of channels to be read
    %
    %   OUTPUT
    %   ===================================================================
    %   analogData      : (nxm) array of data points for n channels
    %   timeVec         : (1xm) time vector
    %
    %   ACN created 11/16 
    %   ACN modified 2/17
    
    DEFINE_CONSTANTS
    stimChan = [];
    END_DEFINE_CONSTANTS
    
    stimData  = struct;
    stimData.timeStamp = cell(1,length(stimChan));
    stimData.data =  cell(1,length(stimChan));
    stimData.dataSize =  cell(1,length(stimChan));
    
    [~,tmp,~] = fileparts(fileparts(dataPath));
    tmp2 = strsplit(tmp,' ');
    catName = tmp2{1};
    
    if exist(fullfile(dataPath,sprintf('datafile%04d.ns5',NEVfilenum)), 'file') == 2
        completeFilePath = fullfile(dataPath,sprintf('datafile%04d.ns5',NEVfilenum));
        [~,f,~]=fileparts(completeFilePath);
        NotifierManager.notify('status', 'Processing NEV file: %s', f)
    elseif exist(fullfile(dataPath,sprintf('%s-%04d.ns5',catName,NEVfilenum)), 'file') == 2
        completeFilePath = fullfile(dataPath,sprintf('%s-%04d.ns5',catName,NEVfilenum));
        [~,f,~]=fileparts(completeFilePath);
        NotifierManager.notify('status', 'Processing NEV file: %s', f)
    else
        completeFilePath = 999;
        NotifierManager.notify('warning', 'Could not find NEV file: %s', f)
    end
    
    
    if completeFilePath ~= 999
        % Open the file and extract some basic information
        [~, hFile] = ns_OpenFile(completeFilePath);
        if isempty(stimChan)
            stimChan = [hFile.Entity(cellfun(@(x) ~isempty(strfind(x, 'stim')), {hFile.Entity.Label})).ElectrodeID]-5120;
        end
        for iChan = 1:length(stimChan)
            
            entityID = find([hFile.Entity(:).ElectrodeID] == stimChan(iChan) + 5120);
            
            if ~isempty(entityID)
                [~, entityInfo] = ns_GetEntityInfo(hFile, entityID(end));

                NotifierManager.notify('status', 'Reading NEV file: %03d, digital channel: %02d', NEVfilenum, stimChan(iChan))
                numCount = entityInfo.ItemCount;
                stimData.data{iChan} = cell(1, numCount);
                stimData.timeStamp{iChan} = NaN(1, numCount); 
                stimData.dataSize{iChan} = NaN(1, numCount);
                for i = 1:numCount
                    [~, stimData.timeStamp{iChan}(i), stimData.data{iChan}{i}, stimData.dataSize{iChan}(i)] = ns_GetSegmentData(hFile, entityID, i);
                end 
            end
        end
        ns_CloseFile(hFile);
        
    end
end