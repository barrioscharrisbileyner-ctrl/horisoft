const CuentaCobro = require("../models/cuentaCobro.model");

const cuentasCobro = [
    new CuentaCobro(1, 101, "Cuota de administración - Julio 2026", 150000, "2026-07-31"),
    new CuentaCobro(2, 102, "Cuota de administración - Julio 2026", 150000, "2026-07-31"),
];

module.exports = cuentasCobro;
