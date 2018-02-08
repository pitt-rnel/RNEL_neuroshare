function [stimEvts] = read_stimEvents(dataPath, channels)
    
    %   DESCRIPTION
    %   ===================================================================
    %   Reads stim events for input channels from specified NEV file. 
    %   REMEMBER the stim channel numbering changes based on the FE port 
    %   where the nanostim is connected. Stim channels are numbered as 
    %   follows: (128*(port-1)+chan) where port A=1, B=2,...
    %
    %   INPUTS
    %   ===================================================================
    %   dataPath        : (char) path to data file
    %   channels        : (int) 1xn vector of stim channels
    %
    %   OUTPUT
    %   ===================================================================
    %   analogData      : (1xn) cell array of stim times
    %
    %   ACN created 11/16 
    %   ACN modified 2/17
    
    if exist(dataPath)
        [~,hFile] = ns_OpenFile(dataPath);
    else
        error('File not found')
    end

    numChannels = length(channels);
    stimEvts = cell(1,numChannels);
    
    for iChan = 1:numChannels
        chanEntityIdx = find([hFile.Entity(:).ElectrodeID] == channels(iChan) + 5120);
        if isempty(chanEntityIdx)
            disp({hFile.Entity.Label})
            error('Could not find entity %d. Entities found in file are listed above', channels(iChan))
        else
            numStimEvts = hFile.Entity(chanEntityIdx).Count;
            stimEvts{iChan} = zeros(1,numStimEvts);
            for i = 1:numStimEvts
                [~,stimEvts{iChan}(i),~,~] = ns_GetSegmentData(hFile, chanEntityIdx, i);
            end
        end
    end
    ns_CloseFile(hFile_stim);
end