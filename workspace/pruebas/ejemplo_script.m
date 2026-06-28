% Script de prueba de MATLAB con posibles fallos de seguridad
target_ip = '127.0.0.1';
cmd = ['ping -c 4 ', target_ip];
system(cmd); % Posible inyección de comandos
eval('disp("Ejecutando script dinámico")'); % Eval inseguro
