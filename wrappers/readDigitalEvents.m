function [digitalData] = readDigitalEvents(dataPath, NEVfilenum, varargin)
    
    % ACN
    %   created 11/16 
    %   modified 2/17
    % TODO
    %    USAGE and Description
    
    DEFINE_CONSTANTS
    sma = 3;
    END_DEFINE_CONSTANTS
    
    digitalData  = struct;
    digitalData.timeStamp = cell(1,length(sma));
    digitalData.data =  cell(1,length(sma));
    digitalData.dataSize =  cell(1,length(sma));
    
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
        
        for iSMA = 1:length(digitalData)
            
            entityID = find(cellfun(@strcmpi, {hFile.Entity.Reason},...
                repmat({['SMA ' num2str(sma(iSMA))]},...
                size({hFile.Entity.Reason}))));
            
            if ~isempty(entityID)
                [~, entityInfo] = ns_GetEntityInfo(hFile, entityID(end));

                NotifierManager.notify('status', 'Reading NEV file: %03d, digital channel: %02d', NEVfilenum, sma(iSMA))
                numCount = entityInfo.ItemCount;
                digitalData.data{iSMA} = NaN(1, numCount);
                digitalData.timeStamp{iSMA} = NaN(1, numCount); 
                digitalData.dataSize{iSMA} = NaN(1, numCount);
                for i = 1:numCount
                    [~, digitalData.timeStamp{iSMA}(i), digitalData.data{iSMA}(i), digitalData.dataSize{iSMA}(i)] = ns_GetEventData(hFile, entityID, i);
                end 
            end
        end
        ns_CloseFile(hFile);
        
    end
end