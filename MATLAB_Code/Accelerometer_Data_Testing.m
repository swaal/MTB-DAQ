%% Accelerometer_Data_Testing.m
%=========================================================================
% ABOUT:
% This code interprets the binary data saved from the ADXL375BCCZ
% accelerometer using the "Convert_ADXL375_Data" function and then plots 
% the results.
%=========================================================================
% WRITTEN BY: Steven Waal
% DATE: 02.29.2021
%=========================================================================
% NOTES:
%   02.29.2021 - File created (SRW).
%==========================================================================

% Clear statements
clear all;
close all;
clc;

% Set the filepath here!
filePath = "/Volumes/DATA/log/data1.bin"; % Filepath to where the binary data file is stored
frequency = 1600; % [Hz] Frequency of the accelerometers

% Run "Convert_ADXL375_Data" function
out = Convert_ADXL375_Data(filePath, frequency);

% Rename outputs for clarity
time        = out(:,1);
x1          = out(:,2);
y1          = out(:,3);
z1          = out(:,4);
x2          = out(:,5);
y2          = out(:,6);
z2          = out(:,7);

% Plot data
figure
plot(time, x1, time, y1, time, z1);
legend('X', 'Y', 'Z');
xlabel('Time, sec');
ylabel('Acceleration, g');
title('Accelerometer 1');

figure
plot(time, x2, time, y2, time, z2);
legend('X', 'Y', 'Z');
xlabel('Time, sec');
ylabel('Acceleration, g');
title('Accelerometer 2');



