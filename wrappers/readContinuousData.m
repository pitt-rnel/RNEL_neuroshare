function [analogData] = readContinuousData(dataPath, NEVfilenum, varargin)
    
    % ACN
    %   created 11/16 
    %   modified 2/17
    
    DEFINE_CONSTANTS
    cuffChans = [];
    emgChans = [];
    END_DEFINE_CONSTANTS

    dataChannels = [{cuffChans} {emgChans}];
    
    analogData = struct;
    analogData.cuffChans = cell(1,length(cuffChans));
    analogData.emgChans = cell(1,length(emgChans));
    
    [~,tmp,~]=fileparts(fileparts(dataPath));
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

        for iType = 1:length(dataChannels)
            for iChan = 1:length(dataChannels{iType})
                NotifierManager.notify('status', 'Reading NEV file: %03d, channel: %02d', NEVfilenum, dataChannels{iType}(iChan))
                EntityIndices = find([hFile.Entity(:).ElectrodeID] == dataChannels{iType}(iChan));                   
                fileTypeNum = hFile.Entity(EntityIndices(end)).FileType;
                fileType = hFile.FileInfo(fileTypeNum).Type;  
                if strcmp('ns5', fileType); cuffEntityID = EntityIndices(end); end   

    %             [ns_RESULT, analogInfo] = ns_GetAnalogInfo(hFile, cuffEntityID);     % analog info contains things like range and sampling rate

                TimeStamps = hFile.FileInfo(hFile.Entity(cuffEntityID).FileType).TimeStamps;
                startIndex = 1;
                indexCount = TimeStamps(2,1);
                if iType == 1
                    [~, ~, analogData.cuffChans{iChan}] = ns_GetAnalogData(hFile, cuffEntityID, startIndex, indexCount);  % 10 ms
%                     analogData.cuffChans{iChan}(analogData.cuffChans{iChan}<-2000 | analogData.cuffChans{iChan}>2000)=[];                            % sometimes the EMG/ENG has a huge spike/blanking =8192
                else
                    [~, ~, analogData.emgChans{iChan}] = ns_GetAnalogData(hFile, cuffEntityID, startIndex, indexCount);  % 10 ms
%                     analogData.emgChans{iChan}(analogData.emgChans{iChan}<-2000 | analogData.emgChans{iChan}>2000)=[];
                end
            end
        end
        ns_CloseFile(hFile);
    else
        analogData.emgChans{1}=[];
    end
end