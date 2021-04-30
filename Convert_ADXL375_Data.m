%% Convert_ADXL375_Data.m
%=========================================================================
% ABOUT:
% This function interprets the binary data saved from the ADXL375BCCZ
% accelerometer.
%=========================================================================
% ARGUMENTS:
%   filePath        = The filepath to the binary file.
%
%   frequency       = The frequency at which the data was collected.
%=========================================================================
% OUTPUTS:
%   out             = [time, x_acceleration_1, y_acceleration_1, z_acceleration_1, x_acceleration_2, y_acceleration_2, z_acceleration_2];
%                      The interpreted data from both accelerometers (1 and
%                      2) for the x, y, and z axes.
%=========================================================================
% WRITTEN BY: Steven Waal
% DATE: 05.06.2019
%=========================================================================
% NOTES:
%   05.06.2019 - File created (SRW). Referenced EOM_2DOF (older version). 
%                (SRW)
%   09.12.2020 - Cleaned up code and added more comments. (SRW)
%=========================================================================

function out = Convert_ADXL375_Data(filePath, frequency)

% CONSTANTS
SCALE_FACTOR = 0.0488;          % [g/LSB] (see ADXL375 data sheet)

% Open binary data file from MTB DAQ
file = fopen(filePath);

% Read binary data from file and store in variable 'data'
data = fread(file);

% Close binary data file
fclose(file);

data = reshape(data, 14, []);

% Decode data

% Add LSBs and MSBs together to reconstruct X, Y, and Z data
x1 = data(2,:) + 256*data(3,:);
y1 = data(4,:) + 256*data(5,:);
z1 = data(6,:) + 256*data(7,:);

x2 = data(9,:) + 256*data(10,:);
y2 = data(11,:) + 256*data(12,:);
z2 = data(13,:) + 256*data(14,:);

% Take two's complement to get sign of data
for i=1:length(x1)
    if x1(i)>32767
        x1(i)=x1(i)-65536;
    end
    if y1(i)>32767
        y1(i)=y1(i)-65536;
    end
    if z1(i)>32767
        z1(i)=z1(i)-65536;
    end
    if x2(i)>32767
        x2(i)=x2(i)-65536;
    end
    if y2(i)>32767
        y2(i)=y2(i)-65536;
    end
    if z2(i)>32767
        z2(i)=z2(i)-65536;
    end
end

x1 = x1.*SCALE_FACTOR;
y1 = y1.*SCALE_FACTOR;
z1 = z1.*SCALE_FACTOR;
x2 = x2.*SCALE_FACTOR;
y2 = y2.*SCALE_FACTOR;
z2 = z2.*SCALE_FACTOR;

time = [0: 1/frequency: (length(x1)-1)/frequency];

% Output the acceleration values, in g's
out = [time', x1', y1', z1', x2', y2', z2'];

% % Plot for testing...
% figure
% plot(time, x1, time, y1, time, z1)
% legend('x', 'y', 'z')
% ylabel('g')
% xlabel('time')

end