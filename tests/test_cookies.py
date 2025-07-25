import requests
import time
import os
from urllib.parse import urlparse, parse_qs

def test_cookie_tracking(base_url="http://127.0.0.1:8000", tag="cookie-test"):
    """Test cookie-based visit tracking"""
    print(f"🍪 Testing cookie-based visit tracking for tag: {tag}")
    print(f"🌐 Base URL: {base_url}")
    print("=" * 60)
    
    # Headers to prevent caching
    no_cache_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    # Test 1: First visit (should create cookie and increment)
    print("\n📍 Test 1: First visit (no cookie)")
    session1 = requests.Session()
    session1.headers.update(no_cache_headers)
    
    response1 = session1.get(f"{base_url}/badge", params={
        'tag': tag,
        'label': 'visits',
        'color': '4ade80',
        'style': 'flat'
    }, allow_redirects=False)
    
    print(f"   Status Code: {response1.status_code}")
    print(f"   Redirect Location: {response1.headers.get('Location', 'None')}")
    print(f"   Cookies Set: {dict(response1.cookies)}")
    
    # Check if visitor_id cookie was set
    visitor_cookie = response1.cookies.get('visitor_id')
    if visitor_cookie:
        print(f"   ✅ Cookie 'visitor_id' set: {visitor_cookie[:8]}...")
    else:
        print("   ❌ No 'visitor_id' cookie found!")
        return False
    
    # Extract visit count from redirect URL
    visit_count1 = None
    if response1.status_code in [302, 307]:  # Accept both redirect codes
        redirect_url = response1.headers.get('Location')
        if redirect_url and 'shields.io' in redirect_url:
            # Parse the shields.io URL to extract visit count
            parts = redirect_url.split('-')
            if len(parts) >= 2:
                try:
                    count_part = parts[-1].split('.svg')[0].split('?')[0]
                    visit_count1 = int(count_part)
                    print(f"   ✅ Visit count from badge: {visit_count1}")
                except:
                    print("   ⚠️  Could not parse visit count from redirect URL")
                    visit_count1 = None
            else:
                visit_count1 = None
        else:
            print("   ❌ Expected redirect to shields.io")
            return False
    else:
        print(f"   ❌ Expected 302/307 redirect, got {response1.status_code}")
        return False
    
    time.sleep(1)  # Small delay between requests
    
    # Test 2: Second visit with same cookie (should NOT increment)
    print("\n📍 Test 2: Second visit with same cookie")
    response2 = session1.get(f"{base_url}/badge", params={
        'tag': tag,
        'label': 'visits',
        'color': '4ade80',
        'style': 'flat'
    }, allow_redirects=False)
    
    print(f"   Status Code: {response2.status_code}")
    print(f"   Cookies in response: {dict(response2.cookies)}")
    
    # Check that the same cookie is still valid
    visit_count2 = None
    if response2.status_code in [302, 307]:
        redirect_url2 = response2.headers.get('Location')
        if redirect_url2 and 'shields.io' in redirect_url2:
            parts = redirect_url2.split('-')
            if len(parts) >= 2:
                try:
                    count_part = parts[-1].split('.svg')[0].split('?')[0]
                    visit_count2 = int(count_part)
                    print(f"   ✅ Visit count from badge: {visit_count2}")
                    if visit_count1 and visit_count2 == visit_count1:
                        print("   ✅ Count did NOT increment (correct behavior)")
                    else:
                        print(f"   ❌ Count changed from {visit_count1} to {visit_count2} (should stay same)")
                except:
                    print("   ⚠️  Could not parse visit count from redirect URL")
        else:
            print("   ❌ Expected redirect to shields.io")
            return False
    
    time.sleep(1)
    
    # Test 3: Third visit with new session (no cookie, should increment)
    print("\n📍 Test 3: Third visit with new session (no cookie)")
    session2 = requests.Session()
    session2.headers.update(no_cache_headers)
    
    response3 = session2.get(f"{base_url}/badge", params={
        'tag': tag,
        'label': 'visits',
        'color': '4ade80',
        'style': 'flat'
    }, allow_redirects=False)
    
    print(f"   Status Code: {response3.status_code}")
    print(f"   Cookies Set: {dict(response3.cookies)}")
    
    # Check if a new visitor_id cookie was set
    new_visitor_cookie = response3.cookies.get('visitor_id')
    if new_visitor_cookie:
        print(f"   ✅ New cookie 'visitor_id' set: {new_visitor_cookie[:8]}...")
        if new_visitor_cookie != visitor_cookie:
            print("   ✅ New cookie is different from first (correct)")
        else:
            print("   ❌ New cookie is same as first (should be different)")
    else:
        print("   ❌ No 'visitor_id' cookie found in new session!")
    
    # Check visit count increment
    visit_count3 = None
    if response3.status_code in [302, 307]:
        redirect_url3 = response3.headers.get('Location')
        if redirect_url3 and 'shields.io' in redirect_url3:
            parts = redirect_url3.split('-')
            if len(parts) >= 2:
                try:
                    count_part = parts[-1].split('.svg')[0].split('?')[0]
                    visit_count3 = int(count_part)
                    print(f"   ✅ Visit count from badge: {visit_count3}")
                    if visit_count1 and visit_count3 == visit_count1 + 1:
                        print("   ✅ Count incremented correctly")
                    else:
                        print(f"   ❌ Count should be {visit_count1 + 1}, got {visit_count3}")
                except:
                    print("   ⚠️  Could not parse visit count from redirect URL")
        else:
            print("   ❌ Expected redirect to shields.io")
    
    time.sleep(1)
    
    # Test 4: Fourth visit with second session cookie (should NOT increment)
    print("\n📍 Test 4: Fourth visit with second session cookie")
    response4 = session2.get(f"{base_url}/badge", params={
        'tag': tag,
        'label': 'visits',
        'color': '4ade80',
        'style': 'flat'
    }, allow_redirects=False)
    
    print(f"   Status Code: {response4.status_code}")
    
    if response4.status_code in [302, 307]:
        redirect_url4 = response4.headers.get('Location')
        if redirect_url4 and 'shields.io' in redirect_url4:
            parts = redirect_url4.split('-')
            if len(parts) >= 2:
                try:
                    count_part = parts[-1].split('.svg')[0].split('?')[0]
                    visit_count4 = int(count_part)
                    print(f"   ✅ Visit count from badge: {visit_count4}")
                    if visit_count3 and visit_count4 == visit_count3:
                        print("   ✅ Count did NOT increment with existing cookie (correct)")
                    else:
                        print(f"   ❌ Count changed from {visit_count3} to {visit_count4} (should stay same)")
                except:
                    print("   ⚠️  Could not parse visit count from redirect URL")
    
    # Test 5: Check stats API
    print("\n📍 Test 5: Checking stats API")
    stats_response = session1.get(f"{base_url}/api/stats/{tag}")
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        print(f"   ✅ Stats API response: {stats_data}")
        expected_count = 2  # Should be 2 visits (first session + second session)
        if stats_data.get('visit_count') == expected_count:
            print(f"   ✅ Stats API shows correct count: {expected_count}")
        else:
            print(f"   ❌ Stats API shows {stats_data.get('visit_count')}, expected {expected_count}")
    else:
        print(f"   ❌ Stats API failed with status {stats_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 Cookie tracking test completed!")
    return True

def test_cache_headers(base_url="http://127.0.0.1:8000"):
    """Test that no-cache headers are properly set"""
    print("\n🚫 Testing cache headers")
    print("=" * 30)
    
    response = requests.get(f"{base_url}/badge", params={
        'tag': 'cache-test',
        'label': 'visits'
    }, allow_redirects=False)
    
    print(f"Status Code: {response.status_code}")
    print("Response Headers:")
    for header, value in response.headers.items():
        if 'cache' in header.lower() or header.lower() in ['pragma', 'expires']:
            print(f"  {header}: {value}")
    
    # Check for proper no-cache headers
    cache_control = response.headers.get('Cache-Control', '')
    pragma = response.headers.get('Pragma', '')
    expires = response.headers.get('Expires', '')
    
    if 'no-cache' in cache_control and 'no-store' in cache_control:
        print("✅ Proper Cache-Control headers set")
    else:
        print(f"⚠️  Cache-Control: {cache_control}")
    
    if pragma == 'no-cache':
        print("✅ Proper Pragma header set")
    else:
        print(f"⚠️  Pragma: {pragma}")
    
    if expires == '0':
        print("✅ Proper Expires header set")
    else:
        print(f"⚠️  Expires: {expires}")

if __name__ == "__main__":
    print("🧪 BadgeTrack Cookie Testing Suite")
    print("===================================")
    
    # Check if server is running
    try:
        health_response = requests.get("http://127.0.0.1:8000/health", timeout=3)
        if health_response.status_code == 200:
            print("✅ Server is running!")
        else:
            print(f"⚠️  Server responded with status {health_response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running at http://127.0.0.1:8000")
        print("   Please start the server with: python wsgi.py")
        exit(1)
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        exit(1)
    
    # Run tests
    try:
        test_cache_headers()
        test_cookie_tracking()
        print("\n🎉 All tests completed!")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
