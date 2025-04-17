import os
import sys
import json
import glob
import traceback

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from teach_assit.core.analysis.static_analyzer import StaticAnalyzer
    from teach_assit.core.analysis.models import ExerciseConfig
    print("Successfully imported modules")
except ImportError as e:
    print(f"Error importing modules: {e}")
    traceback.print_exc()
    sys.exit(1)

def main():
    try:
        # Check if directories exist
        print("Current working directory:", os.getcwd())
        print("Checking if directories exist:")
        print(f"assessments/ exists: {os.path.exists('assessments')}")
        print(f"configs/ exists: {os.path.exists('configs')}")
        print(f"tests/java_samples/TD1/ exists: {os.path.exists('tests/java_samples/TD1')}")
        
        # List files in TD1 directory
        td1_files = glob.glob('tests/java_samples/TD1/**/*.java', recursive=True)
        print(f"Java files in TD1 directory: {td1_files}")
        
        # Load TD1 configuration
        td1_config_path = os.path.join('assessments', 'TD1.json')
        print(f"TD1 config path: {td1_config_path}")
        print(f"TD1 config exists: {os.path.exists(td1_config_path)}")
        
        with open(td1_config_path, 'r') as f:
            td1_config = json.load(f)
        
        print(f"TD1 config loaded: {td1_config}")
        
        # Find exercise ID for intervalle
        intervalle_id = None
        for exercise in td1_config['exercises']:
            if exercise['exerciseId'] == '02-intervalle':
                intervalle_id = exercise['exerciseId']
                break
        
        if not intervalle_id:
            print("Exercise '02-intervalle' not found in TD1.json configuration")
            return
        
        # Load exercise config
        exercise_config_path = os.path.join('configs', f'{intervalle_id}.json')
        print(f"Exercise config path: {exercise_config_path}")
        print(f"Exercise config exists: {os.path.exists(exercise_config_path)}")
        
        with open(exercise_config_path, 'r') as f:
            config_dict = json.load(f)
        
        # Print required methods from config for clarity
        if 'rules' in config_dict and 'requiredMethods' in config_dict['rules']:
            print("\nRequired methods from config:")
            for method in config_dict['rules']['requiredMethods']:
                params = ', '.join(method.get('params', []))
                print(f"  - {method['name']}({params}) -> {method.get('returnType', 'void')}")
        
        config = ExerciseConfig(config_dict)
        
        # Initialize analyzer
        analyzer = StaticAnalyzer()
        
        # Find all Java files in the TD1 directory
        java_files = glob.glob('tests/java_samples/TD1/**/*.java', recursive=True)
        
        print(f"\nFound {len(java_files)} Java files to analyze")
        
        # Prepare results summary
        summary = {
            'total_files': len(java_files),
            'valid_files': 0,
            'files_with_syntax_errors': 0,
            'files_with_missing_methods': 0,
            'fully_compliant_files': 0
        }
        
        # Analyze each file
        for java_file in java_files:
            student_name = os.path.basename(os.path.dirname(java_file))
            print(f"\n===== Analyzing file: {java_file} (Student: {student_name}) =====")
            
            # Read the Java code
            with open(java_file, 'r', encoding='utf-8') as f:
                java_code = f.read()
            
            # Run the analysis
            result = analyzer.analyze_code(java_code, config)
            
            is_valid_syntax = len(result['syntax_errors']) == 0
            has_all_methods = len(result['missing_methods']) == 0
            
            # Update summary
            if result['is_valid']:
                summary['valid_files'] += 1
            if not is_valid_syntax:
                summary['files_with_syntax_errors'] += 1
            if not has_all_methods:
                summary['files_with_missing_methods'] += 1
            if is_valid_syntax and has_all_methods:
                summary['fully_compliant_files'] += 1
            
            # Print results
            print(f"Is valid code: {result['is_valid']}")
            
            if result['syntax_errors']:
                print(f"Syntax errors: {len(result['syntax_errors'])}")
                for error in result['syntax_errors']:
                    print(f"  - Line {error.get('line', 'unknown')}: {error.get('message', 'Unknown error')}")
            else:
                print("No syntax errors found")
            
            if result['missing_methods']:
                print(f"Missing methods: {len(result['missing_methods'])}")
                for method in result['missing_methods']:
                    params = ', '.join(method.get('params', []))
                    print(f"  - {method['name']}({params}) -> {method.get('expected_return', 'N/A')}")
            else:
                print("All required methods found")
            
            if 'analysis_details' in result and 'found_methods' in result['analysis_details']:
                print("Found methods:")
                for method in result['analysis_details']['found_methods']:
                    print(f"  - {method}")
            
            # Print additional analysis details if available
            if 'analysis_details' in result:
                details = result['analysis_details']
                
                if 'custom_pattern_results' in details:
                    print("\nCustom pattern results:")
                    for pattern_result in details['custom_pattern_results']:
                        status = "Found" if pattern_result.get('found', False) else "Not found"
                        print(f"  - {pattern_result.get('description', 'Unknown pattern')}: {status}")
                
                if 'operator_usage' in details:
                    print("\nOperator usage:")
                    for operator, count in details['operator_usage'].items():
                        print(f"  - {operator}: {count} times")
        
        # Print summary
        print("\n===== Summary =====")
        print(f"Total files analyzed: {summary['total_files']}")
        print(f"Files with valid code: {summary['valid_files']}")
        print(f"Files with syntax errors: {summary['files_with_syntax_errors']}")
        print(f"Files with missing methods: {summary['files_with_missing_methods']}")
        print(f"Fully compliant files: {summary['fully_compliant_files']}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main() 