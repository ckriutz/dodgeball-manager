"""
Unit tests for skill distribution validation and player generation.

Tests the validate_skill_distribution and distribute_skill_points functions
from services/utils.py to ensure correct skill allocation and validation.

Test Coverage:
- Skill distribution validation: sum must equal 10 for new players
- Individual skill range validation: each skill 0-100
- Required skill presence: all 6 skills must exist
- Random distribution: distribute_skill_points generates valid distributions
- Edge cases: missing skills, extra skills, out-of-range values

References:
- FR-002: Sum of all skills must equal 10 for new players
- FR-003: Each skill must be 0-100
- data-model.md: Player.skills validation rules
- research.md: Skill distribution mechanism
"""

import pytest
from src.services.utils import validate_skill_distribution, distribute_skill_points


class TestSkillDistributionValidation:
    """Test suite for skill distribution validation."""
    
    def test_valid_skill_distribution(self):
        """Test that a valid 10-point distribution passes validation."""
        # Arrange: Standard valid distribution
        skills = {
            'catching': 2,
            'throwing': 2,
            'dodging': 2,
            'speed': 2,
            'iq': 1,
            'luck': 1
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills)
        
        # Assert
        assert is_valid is True
        assert error_msg == ""
    
    def test_all_skills_at_minimum(self):
        """Test distribution with all skills at 0 (edge case)."""
        skills = {
            'catching': 0,
            'throwing': 0,
            'dodging': 0,
            'speed': 0,
            'iq': 0,
            'luck': 0
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills, total_required=0)
        
        # Assert
        assert is_valid is True
        assert error_msg == ""
    
    def test_concentrated_skill_distribution(self):
        """Test distribution with points concentrated in fewer skills."""
        skills = {
            'catching': 5,
            'throwing': 5,
            'dodging': 0,
            'speed': 0,
            'iq': 0,
            'luck': 0
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills)
        
        # Assert
        assert is_valid is True
    
    def test_uneven_distribution(self):
        """Test valid but uneven skill distribution."""
        skills = {
            'catching': 4,
            'throwing': 3,
            'dodging': 1,
            'speed': 1,
            'iq': 1,
            'luck': 0
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills)
        
        # Assert
        assert is_valid is True


class TestSkillDistributionValidationFailures:
    """Test suite for skill distribution validation failures."""
    
    def test_skill_sum_too_low(self):
        """Test that sum below 10 fails validation."""
        skills = {
            'catching': 1,
            'throwing': 1,
            'dodging': 1,
            'speed': 1,
            'iq': 1,
            'luck': 1
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills)
        
        # Assert
        assert is_valid is False
        assert "Skill sum is 6 but required sum is 10" in error_msg
    
    def test_skill_sum_too_high(self):
        """Test that sum above 10 fails validation."""
        skills = {
            'catching': 3,
            'throwing': 3,
            'dodging': 3,
            'speed': 3,
            'iq': 3,
            'luck': 3
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills)
        
        # Assert
        assert is_valid is False
        assert "Skill sum is 18 but required sum is 10" in error_msg
    
    def test_missing_required_skill(self):
        """Test that missing a required skill fails validation."""
        skills = {
            'catching': 2,
            'throwing': 2,
            'dodging': 2,
            'speed': 2,
            'iq': 2
            # 'luck' is missing
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills)
        
        # Assert
        assert is_valid is False
        assert "Missing skills" in error_msg
        assert "luck" in error_msg
    
    def test_extra_skill_present(self):
        """Test that extra skills fail validation."""
        skills = {
            'catching': 2,
            'throwing': 2,
            'dodging': 2,
            'speed': 2,
            'iq': 1,
            'luck': 1,
            'charisma': 5  # Extra skill not in spec
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills)
        
        # Assert
        assert is_valid is False
        assert "Extra skills" in error_msg
        assert "charisma" in error_msg
    
    def test_skill_value_negative(self):
        """Test that negative skill values fail validation (FR-003)."""
        skills = {
            'catching': -1,
            'throwing': 3,
            'dodging': 3,
            'speed': 3,
            'iq': 1,
            'luck': 1
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills)
        
        # Assert
        assert is_valid is False
        assert "catching" in error_msg
        assert "outside range [0, 100]" in error_msg
    
    def test_skill_value_exceeds_maximum(self):
        """Test that skill values > 100 fail validation (FR-003)."""
        skills = {
            'catching': 101,
            'throwing': 0,
            'dodging': 0,
            'speed': 0,
            'iq': 0,
            'luck': 0
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills, total_required=101)
        
        # Assert
        assert is_valid is False
        assert "catching" in error_msg
        assert "outside range [0, 100]" in error_msg
    
    def test_multiple_skills_out_of_range(self):
        """Test validation fails on first out-of-range skill found."""
        skills = {
            'catching': -5,
            'throwing': 105,
            'dodging': 2,
            'speed': 2,
            'iq': 1,
            'luck': 1
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills)
        
        # Assert
        assert is_valid is False
        assert "outside range [0, 100]" in error_msg


class TestDistributeSkillPoints:
    """Test suite for random skill point distribution."""
    
    def test_distributes_correct_total(self):
        """Test that distributed points sum to the required total."""
        # Act: Generate multiple distributions
        for _ in range(10):
            skills = distribute_skill_points(total_points=10, num_skills=6)
            
            # Assert: Sum equals 10
            assert sum(skills.values()) == 10
    
    def test_includes_all_required_skills(self):
        """Test that distribution includes all 6 skill types."""
        # Act
        skills = distribute_skill_points(total_points=10, num_skills=6)
        
        # Assert: All skills present
        expected_skills = {'catching', 'throwing', 'dodging', 'speed', 'iq', 'luck'}
        assert set(skills.keys()) == expected_skills
    
    def test_all_values_non_negative(self):
        """Test that no skill receives a negative value."""
        # Act: Generate multiple distributions
        for _ in range(10):
            skills = distribute_skill_points(total_points=10, num_skills=6)
            
            # Assert: All values >= 0
            assert all(value >= 0 for value in skills.values())
    
    def test_distribution_passes_validation(self):
        """Test that generated distributions pass validation."""
        # Act: Generate multiple distributions
        for _ in range(10):
            skills = distribute_skill_points(total_points=10, num_skills=6)
            
            # Assert: Passes validation
            is_valid, error_msg = validate_skill_distribution(skills, total_required=10)
            assert is_valid is True, f"Generated skills failed validation: {error_msg}"
    
    def test_distribution_with_zero_points(self):
        """Test edge case of distributing 0 points."""
        # Act
        skills = distribute_skill_points(total_points=0, num_skills=6)
        
        # Assert: All skills are 0
        assert all(value == 0 for value in skills.values())
        assert sum(skills.values()) == 0
    
    def test_distribution_with_large_total(self):
        """Test distribution with higher point totals."""
        # Act
        skills = distribute_skill_points(total_points=30, num_skills=6)
        
        # Assert
        assert sum(skills.values()) == 30
        assert all(value >= 0 for value in skills.values())
    
    def test_distribution_creates_variety(self):
        """Test that multiple calls produce different distributions."""
        # Act: Generate multiple distributions
        distributions = []
        for _ in range(10):
            skills = distribute_skill_points(total_points=10, num_skills=6)
            distributions.append(tuple(sorted(skills.values())))
        
        # Assert: At least some variety (not all identical)
        # Note: There's a small chance this could fail due to randomness
        unique_distributions = set(distributions)
        assert len(unique_distributions) > 1, "All distributions were identical"
    
    def test_distribution_individual_values_reasonable(self):
        """Test that individual skill values don't exceed total."""
        # Act: Generate multiple distributions
        for _ in range(20):
            skills = distribute_skill_points(total_points=10, num_skills=6)
            
            # Assert: No individual skill exceeds total
            assert all(value <= 10 for value in skills.values())
    
    def test_invalid_num_skills_raises_error(self):
        """Test that incorrect num_skills parameter raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="num_skills must be 6"):
            distribute_skill_points(total_points=10, num_skills=5)
    
    def test_distribution_with_single_point(self):
        """Test distributing just 1 point among skills."""
        # Act
        skills = distribute_skill_points(total_points=1, num_skills=6)
        
        # Assert
        assert sum(skills.values()) == 1
        assert sum(1 for v in skills.values() if v == 1) == 1  # Exactly one skill has 1
        assert sum(1 for v in skills.values() if v == 0) == 5  # Five skills have 0


class TestSkillDistributionEdgeCases:
    """Test edge cases for skill distribution validation and generation."""
    
    def test_validation_with_custom_total(self):
        """Test validation with non-standard total requirement."""
        skills = {
            'catching': 10,
            'throwing': 10,
            'dodging': 0,
            'speed': 0,
            'iq': 0,
            'luck': 0
        }
        
        # Act: Validate with total of 20
        is_valid, error_msg = validate_skill_distribution(skills, total_required=20)
        
        # Assert
        assert is_valid is True
    
    def test_validation_boundary_at_100(self):
        """Test skill value exactly at maximum boundary."""
        skills = {
            'catching': 100,
            'throwing': 0,
            'dodging': 0,
            'speed': 0,
            'iq': 0,
            'luck': 0
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills, total_required=100)
        
        # Assert
        assert is_valid is True
    
    def test_validation_boundary_at_zero(self):
        """Test skill values exactly at minimum boundary."""
        skills = {
            'catching': 0,
            'throwing': 0,
            'dodging': 0,
            'speed': 0,
            'iq': 0,
            'luck': 10
        }
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills)
        
        # Assert
        assert is_valid is True
    
    def test_empty_skills_dict_fails(self):
        """Test that empty skills dictionary fails validation."""
        skills = {}
        
        # Act
        is_valid, error_msg = validate_skill_distribution(skills)
        
        # Assert
        assert is_valid is False
        assert "Missing skills" in error_msg
    
    def test_distribution_determinism_with_seed(self):
        """Test that setting random seed produces deterministic results."""
        import random
        
        # Act: Generate with same seed twice
        random.seed(42)
        skills1 = distribute_skill_points(total_points=10, num_skills=6)
        
        random.seed(42)
        skills2 = distribute_skill_points(total_points=10, num_skills=6)
        
        # Assert: Identical distributions
        assert skills1 == skills2
