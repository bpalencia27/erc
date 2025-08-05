/**
 * Módulo para visualizaciones avanzadas de datos clínicos
 */

// Gráfico de tendencia de TFG a lo largo del tiempo
function createTFGTrendChart(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Extraer fechas y valores de TFG
    const dates = data.map(item => new Date(item.fecha));
    const values = data.map(item => item.tfg);
    
    // Crear configuración para ApexCharts
    const options = {
        series: [{
            name: 'TFG (mL/min)',
            data: values
        }],
        chart: {
            type: 'line',
            height: 300,
            toolbar: {
                show: false
            },
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 800
            }
        },
        stroke: {
            curve: 'smooth',
            width: 3
        },
        colors: ['#2563eb'],
        markers: {
            size: 5,
            hover: {
                size: 7
            }
        },
        xaxis: {
            type: 'datetime',
            categories: dates,
            labels: {
                formatter: function(value) {
                    return new Date(value).toLocaleDateString();
                }
            }
        },
        yaxis: {
            title: {
                text: 'TFG (mL/min)'
            },
            min: 0,
            max: Math.max(...values) + 10,
            forceNiceScale: true
        },
        annotations: {
            yaxis: [
                {
                    y: 90,
                    y2: 60,
                    borderColor: '#84cc16',
                    fillColor: '#84cc16',
                    opacity: 0.1,
                    label: {
                        text: 'G1-G2',
                        position: 'left',
                        offsetX: 10,
                        style: {
                            color: '#84cc16',
                            background: 'transparent'
                        }
                    }
                },
                {
                    y: 60,
                    y2: 30,
                    borderColor: '#f59e0b',
                    fillColor: '#f59e0b',
                    opacity: 0.1,
                    label: {
                        text: 'G3',
                        position: 'left',
                        offsetX: 10,
                        style: {
                            color: '#f59e0b',
                            background: 'transparent'
                        }
                    }
                },
                {
                    y: 30,
                    y2: 15,
                    borderColor: '#ef4444',
                    fillColor: '#ef4444',
                    opacity: 0.1,
                    label: {
                        text: 'G4',
                        position: 'left',
                        offsetX: 10,
                        style: {
                            color: '#ef4444',
                            background: 'transparent'
                        }
                    }
                },
                {
                    y: 15,
                    y2: 0,
                    borderColor: '#b91c1c',
                    fillColor: '#b91c1c',
                    opacity: 0.1,
                    label: {
                        text: 'G5',
                        position: 'left',
                        offsetX: 10,
                        style: {
                            color: '#b91c1c',
                            background: 'transparent'
                        }
                    }
                }
            ]
        },
        tooltip: {
            x: {
                format: 'dd MMM yyyy'
            },
            y: {
                formatter: function (val) {
                    return val + ' mL/min';
                }
            }
        }
    };
    
    const chart = new ApexCharts(container, options);
    chart.render();
    
    return chart;
}

// Gráfico de progreso de metas terapéuticas
function createGoalsProgressChart(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Preparar datos
    const categories = data.map(item => item.parametro);
    const actual = data.map(item => item.valor_actual);
    const metas = data.map(item => item.meta);
    const cumple = data.map(item => item.cumple);
    
    // Colores según cumplimiento
    const colors = cumple.map(c => c ? '#22c55e' : '#ef4444');
    
    // Configuración de ApexCharts
    const options = {
        series: [{
            name: 'Valor Actual',
            data: actual
        }, {
            name: 'Meta',
            data: metas
        }],
        chart: {
            type: 'bar',
            height: 350,
            stacked: false,
            toolbar: {
                show: false
            }
        },
        colors: ['#3b82f6', '#22c55e'],
        plotOptions: {
            bar: {
                horizontal: true,
                columnWidth: '55%',
                endingShape: 'rounded',
                dataLabels: {
                    position: 'top',
                }
            },
        },
        dataLabels: {
            enabled: true,
            formatter: function (val) {
                return val;
            },
            offsetX: 20
        },
        stroke: {
            width: 0
        },
        xaxis: {
            categories: categories,
        },
        legend: {
            position: 'top'
        },
        fill: {
            opacity: 1
        }
    };
    
    const chart = new ApexCharts(container, options);
    chart.render();
    
    return chart;
}

// Gráfico de radar para comparar valores actuales con metas
function createRadarComparisonChart(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Preparar datos
    const categories = data.map(item => item.parametro);
    const valorActualNormalizado = data.map(item => {
        // Normalizar valores para comparación en radar
        const actual = parseFloat(item.valor_actual);
        const meta = parseFloat(item.meta);
        if (isNaN(actual) || isNaN(meta)) return 0;
        
        // Si la meta es "menor que", invertimos la normalización
        if (item.tipo_meta === 'menor_que') {
            return meta === 0 ? 0 : Math.min(100, (meta / actual) * 100);
        } else {
            return actual === 0 ? 0 : Math.min(100, (actual / meta) * 100);
        }
    });
    
    // Valor objetivo (100% para todos)
    const valorMeta = categories.map(() => 100);
    
    // Configuración del radar
    const options = {
        series: [{
            name: 'Actual (%)',
            data: valorActualNormalizado
        }, {
            name: 'Meta (%)',
            data: valorMeta
        }],
        chart: {
            height: 350,
            type: 'radar',
            toolbar: {
                show: false
            },
            dropShadow: {
                enabled: true,
                blur: 1,
                left: 1,
                top: 1
            }
        },
        colors: ['#3b82f6', '#22c55e'],
        stroke: {
            width: 2
        },
        fill: {
            opacity: 0.1
        },
        markers: {
            size: 4,
            hover: {
                size: 6
            }
        },
        xaxis: {
            categories: categories
        },
        yaxis: {
            max: 100
        }
    };
    
    const chart = new ApexCharts(container, options);
    chart.render();
    
    return chart;
}