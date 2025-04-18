import React, { useState } from 'react';
import { Search, Download, Check, X, AlertTriangle, ChevronDown, Info } from 'lucide-react';

export default function ExercisesDashboard() {
  const [selectedExercise, setSelectedExercise] = useState(null);
  
  // Données simulées basées sur votre capture d'écran
  const students = [
    {
      id: 1,
      name: 'GOGO',
      exercises: [
        {
          id: '09-fonction-racine-carree',
          title: 'Fonction Racine Carrée',
          filename: '09-fonction-racine-carree.java',
          score: '10.0/10',
          verifications: '7/7',
          status: {
            syntax: true,
            method: true,
            structure: true,
            naming: true,
            operators: true,
            patterns: true
          },
          details: {
            methodFound: 'double calculerRacineCarree(double)',
            summary: '7/7 vérifications réussies'
          }
        },
        {
          id: '10-comptage-mots',
          title: 'Comptage de Mots',
          filename: '10-comptage-mots.java',
          score: '8.6/10',
          verifications: '6/7',
          status: {
            syntax: true,
            method: true,
            structure: true,
            naming: true,
            operators: false,
            patterns: true
          },
          details: {
            problems: ['Utilisation d\'opérateurs non autorisés'],
            summary: '6/7 vérifications réussies'
          }
        }
      ]
    },
    {
      id: 2,
      name: 'SAM',
      exercises: [
        {
          id: '09-fonction-racine-carree',
          title: 'Fonction Racine Carrée',
          filename: '09-fonction-racine-carree.java',
          score: '5.7/10',
          verifications: '4/7',
          status: {
            syntax: true,
            method: true,
            structure: false,
            naming: false,
            operators: true,
            patterns: false
          },
          details: {
            methodFound: 'double calculerRacineCarree(double)',
            summary: '4/7 vérifications réussies'
          }
        },
        {
          id: '10-comptage-mots',
          title: 'Comptage de Mots',
          filename: '10-comptage-mots.java',
          score: '7.1/10',
          verifications: '5/7',
          status: {
            syntax: true,
            method: true,
            structure: false,
            naming: false,
            operators: true,
            patterns: true
          },
          details: {
            problems: ['Structure incorrecte', 'Nommage non conforme'],
            summary: '5/7 vérifications réussies'
          }
        }
      ]
    }
  ];

  // Filtre simulé
  const [searchQuery, setSearchQuery] = useState('');
  
  // Stats simulées
  const stats = [
    { label: "Exercices complétés", value: 4 },
    { label: "Exercices en cours", value: 1 },
    { label: "Exercices en échec", value: 0 },
    { label: "Sans tentative", value: 0 }
  ];

  const handleExerciseDetails = (student, exercise) => {
    setSelectedExercise({ student, exercise });
  };

  return (
    <div className="bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Tableau de bord d'évaluation</h1>
        
        {/* Filtres et recherche */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-grow relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={18} className="text-gray-400" />
            </div>
            <input 
              type="text" 
              placeholder="Rechercher par nom d'étudiant ou exercice..." 
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-full focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <div className="flex gap-2">
            <div className="relative inline-block">
              <select className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>Tous les exercices</option>
                <option>Fonction Racine Carrée</option>
                <option>Comptage de Mots</option>
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                <ChevronDown size={16} className="text-gray-500" />
              </div>
            </div>
            
            <div className="relative inline-block">
              <select className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>Toutes les dates</option>
                <option>Cette semaine</option>
                <option>Ce mois</option>
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                <ChevronDown size={16} className="text-gray-500" />
              </div>
            </div>
            
            <button className="bg-green-500 hover:bg-green-600 text-white rounded-lg px-4 py-2 flex items-center gap-2 transition-colors">
              <Download size={18} />
              <span>Exporter</span>
            </button>
          </div>
        </div>
        
        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
              <div className="text-sm text-gray-500 mb-1">{stat.label}</div>
              <div className="text-2xl font-bold">{stat.value}</div>
            </div>
          ))}
        </div>
        
        {/* Tableau principal */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Étudiant
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Exercice
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Résultat
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {students.map(student => (
                  student.exercises.map((exercise, exIndex) => (
                    <tr key={`${student.id}-${exercise.id}`} className={exIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      {exIndex === 0 && (
                        <td rowSpan={student.exercises.length} className="px-6 py-4 whitespace-nowrap align-top">
                          <div className="flex items-center">
                            <div className="text-sm font-medium text-gray-900">
                              {student.name}
                            </div>
                          </div>
                        </td>
                      )}
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 font-medium">{exercise.title}</div>
                        <div className="text-xs text-gray-500">{exercise.filename}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col space-y-1">
                          {Object.entries(exercise.status).map(([key, value]) => (
                            <div key={key} className="flex items-center">
                              {value ? (
                                <Check size={16} className="text-green-500 mr-1" />
                              ) : key === 'patterns' && !value ? (
                                <AlertTriangle size={16} className="text-yellow-500 mr-1" />
                              ) : (
                                <X size={16} className="text-red-500 mr-1" />
                              )}
                              <span className="text-xs capitalize">{key}</span>
                            </div>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm font-medium ${Number(exercise.score.split('/')[0]) >= 7 ? 'text-green-600' : 'text-red-600'}`}>
                          {exercise.verifications} vérifications - {exercise.score} pt
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button 
                          onClick={() => handleExerciseDetails(student, exercise)}
                          className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
                        >
                          <Info size={16} />
                          <span>Détails</span>
                        </button>
                      </td>
                    </tr>
                  ))
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Modal de détails */}
        {selectedExercise && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-full overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-bold">
                    Détails - {selectedExercise.exercise.title}
                  </h3>
                  <button 
                    onClick={() => setSelectedExercise(null)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <X size={20} />
                  </button>
                </div>
                
                <div className="mb-4">
                  <div className="text-sm font-medium text-gray-500 mb-1">Étudiant</div>
                  <div className="text-base">{selectedExercise.student.name}</div>
                </div>
                
                <div className="mb-4">
                  <div className="text-sm font-medium text-gray-500 mb-1">Fichier</div>
                  <div className="text-base">{selectedExercise.exercise.filename}</div>
                </div>
                
                <div className="mb-4">
                  <div className="text-sm font-medium text-gray-500 mb-1">Résultat</div>
                  <div className="text-base font-semibold">
                    {selectedExercise.exercise.details.summary}
                    <span className="ml-2 text-sm text-gray-500">
                      Note estimée: {selectedExercise.exercise.score} points
                    </span>
                  </div>
                </div>
                
                <div className="mb-4">
                  <div className="text-sm font-medium text-gray-500 mb-1">Vérifications</div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                    {Object.entries(selectedExercise.exercise.status).map(([key, value]) => (
                      <div key={key} className={`flex items-center p-2 rounded ${value ? 'bg-green-50' : 'bg-red-50'}`}>
                        {value ? (
                          <Check size={16} className="text-green-500 mr-2" />
                        ) : (
                          <X size={16} className="text-red-500 mr-2" />
                        )}
                        <span className="capitalize">{key}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                {selectedExercise.exercise.details.methodFound && (
                  <div className="mb-4">
                    <div className="text-sm font-medium text-gray-500 mb-1">Méthodes trouvées</div>
                    <div className="bg-gray-50 p-2 rounded border border-gray-200">
                      <code>{selectedExercise.exercise.details.methodFound}</code>
                    </div>
                  </div>
                )}
                
                {selectedExercise.exercise.details.problems && selectedExercise.exercise.details.problems.length > 0 && (
                  <div className="mb-4">
                    <div className="text-sm font-medium text-red-500 mb-1">Problèmes détectés</div>
                    <ul className="list-disc list-inside bg-red-50 p-3 rounded">
                      {selectedExercise.exercise.details.problems.map((problem, i) => (
                        <li key={i} className="text-red-600">{problem}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div className="flex justify-end mt-6">
                  <button 
                    onClick={() => setSelectedExercise(null)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
                  >
                    Fermer
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
