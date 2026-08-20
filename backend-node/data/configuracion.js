const ParametroConfiguracion = require("../models/parametroConfiguracion.model");

const configuracion = [
    new ParametroConfiguracion("nombre_conjunto", "Conjunto Residencial Los Álamos", "Nombre del conjunto"),
    new ParametroConfiguracion("dia_pago_cuota", "5", "Día límite de pago mensual de la cuota de administración"),
    new ParametroConfiguracion("porcentaje_mora", "1.5", "Porcentaje de interés de mora mensual"),
];

module.exports = configuracion;
